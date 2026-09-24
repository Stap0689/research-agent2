#!/usr/bin/env python3
"""Research agent source audit: classify sources, delete hard-rejects, record audit trail.

Portable version for the open-source research-agent. Works with any
notebook-index.json path (configurable via --index-path or NOTEBOOK_INDEX_PATH env var).

Usage:
  source-audit.py --notebook <ID> [--dry-run] [--skip-delete] [--check-markdown]
                  [--index-path <path>]

Actions:
  1. Fetch source list via notebooklm source list --json --notebook <ID>
  2. Domain-match each source against hard-reject patterns (SOURCE-QUALITY.md)
  3. Domain-match against Tier 5 flag patterns
  4. Assign a positive credibility tier (1-3) to recognized authoritative domains
     via DOMAIN_TIER_MAP / SUFFIX_TIER_MAP, so the >=15 Tier 1-3 corpus minimum the
     methodology requires is actually measurable (reporting only -- NON-BLOCKING)
  5. Check MARKDOWN sources for laundered hard-reject references (--check-markdown)
  6. Delete hard-reject sources (unless --dry-run or --skip-delete)
  7. Record per-source classification + tier distribution to notebook-index.json
  8. Set source_audit.completed = true

Hard-reject domains (no exceptions):
  Reddit, StackOverflow, StackExchange, GeeksforGeeks, Scribd, YouTube,
  TikTok, LinkedIn posts/pulse, Twitter/X, Quora, Emergent Mind

See SOURCE-QUALITY.md for the complete 5-tier credibility hierarchy.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VERSION = "1.1"

DEFAULT_INDEX_PATH = Path.home() / "research-agent" / "observability" / "notebook-index.json"

HARD_REJECT_PATTERNS = [
    re.compile(r"(?:^|://)(?:www\.)?reddit\.com"),
    re.compile(r"(?:^|://)(?:www\.)?stackoverflow\.com"),
    re.compile(r"(?:^|://)(?:www\.)?[\w-]*\.stackexchange\.com"),
    re.compile(r"(?:^|://)(?:www\.)?geeksforgeeks\.org"),
    re.compile(r"(?:^|://)(?:www\.)?scribd\.com"),
    re.compile(r"(?:^|://)(?:www\.)?youtube\.com"),
    re.compile(r"(?:^|://)(?:www\.)?youtu\.be"),
    re.compile(r"(?:^|://)(?:www\.)?tiktok\.com"),
    re.compile(r"(?:^|://)(?:www\.)?linkedin\.com/(?:posts|pulse)"),
    re.compile(r"(?:^|://)(?:www\.)?(?:twitter|x)\.com/"),
    re.compile(r"(?:^|://)(?:www\.)?quora\.com"),
    re.compile(r"(?:^|://)(?:www\.)?emergentmind\.com"),
]

TIER5_FLAG_PATTERNS = [
    re.compile(r"(?:^|://)(?:www\.)?dzone\.com"),
    re.compile(r"(?:^|://)(?:www\.)?dev\.to"),
    re.compile(r"(?:^|://)(?:www\.)?hackernoon\.com"),
    re.compile(r"(?:^|://)(?:www\.)?towardsdatascience\.com"),
    re.compile(r"(?:^|://)(?:www\.)?analyticsvidhya\.com"),
]

# Positive tier allowlist (SOURCE-QUALITY.md 5-tier hierarchy). A recognized host is
# assigned Tier 1-3 so the audit can MEASURE the >=15 Tier 1-3 corpus minimum the
# methodology requires. This is reporting only; nothing here blocks Q&A. Unrecognized
# hosts that survive the reject/Tier-5 filters are accepted but tier=None ("unclassified")
# and do NOT count toward the Tier 1-3 total. Matching is suffix-aware.
DOMAIN_TIER_MAP: dict[str, int] = {
    # Tier 1 -- flagship multidisciplinary / systematic-review venues
    "nature.com": 1, "science.org": 1, "pnas.org": 1, "thelancet.com": 1,
    "nejm.org": 1, "jamanetwork.com": 1, "cochranelibrary.com": 1, "cell.com": 1,
    # Tier 2 -- peer-reviewed journals, major publishers, top CS/security venues, think tanks
    "ieee.org": 2, "ieeexplore.ieee.org": 2, "acm.org": 2, "dl.acm.org": 2,
    "springer.com": 2, "link.springer.com": 2, "sciencedirect.com": 2, "wiley.com": 2,
    "onlinelibrary.wiley.com": 2, "tandfonline.com": 2, "cambridge.org": 2, "oup.com": 2,
    "usenix.org": 2, "ndss-symposium.org": 2, "ieee-security.org": 2, "sigsac.org": 2,
    "petsymposium.org": 2, "rand.org": 2, "nationalacademies.org": 2, "nap.edu": 2,
    "neurips.cc": 2, "proceedings.neurips.cc": 2, "mlr.press": 2, "proceedings.mlr.press": 2,
    "aclanthology.org": 2, "openreview.net": 2, "jmlr.org": 2, "aaai.org": 2,
    # Tier 3 -- preprints, government, standards, frameworks, first-party platform docs
    "arxiv.org": 3, "biorxiv.org": 3, "medrxiv.org": 3, "ssrn.com": 3,
    "iso.org": 3, "ietf.org": 3, "rfc-editor.org": 3, "w3.org": 3,
    "who.int": 3, "oecd.org": 3, "worldbank.org": 3, "europa.eu": 3, "enisa.europa.eu": 3,
    "semanticscholar.org": 3, "distill.pub": 3,
    # Tier 3 -- authoritative security threat-intel / TTP frameworks (gov-funded FFRDC,
    # incident-response standards bodies). MITRE ATT&CK is the canonical adversary-TTP
    # taxonomy; FIRST publishes CVSS and IR standards; CISA/NIST are US-gov standards.
    "attack.mitre.org": 3, "mitre.org": 3, "first.org": 3, "cisa.gov": 3, "nist.gov": 3,
    # Tier 3 -- first-party platform engineering docs (vendor-published but normative,
    # no sales function)
    "learn.microsoft.com": 3, "docs.microsoft.com": 3, "developer.apple.com": 3,
    "kernel.org": 3, "docs.kernel.org": 3, "blackhat.com": 3,
}

# Structural suffix tiers (checked after the exact/suffix domain map). Government,
# military, international-org, and academic TLDs are Tier 3 authoritative by institution.
SUFFIX_TIER_MAP: list[tuple[str, int]] = [
    (".gov", 3), (".mil", 3), (".int", 3), (".edu", 3),
]

GENERIC_TITLE_RE = re.compile(
    r"^(?:The |A |An |Advancing |Synergistic |Systems |Comprehensive |Cognitive )"
    r"|(?:Architecture|Framework|Overview|Survey|Analysis) (?:of|for|in) ",
    re.IGNORECASE,
)

HARD_REJECT_CONTENT_PATTERNS = [
    re.compile(r"reddit\.com/r/", re.IGNORECASE),
    re.compile(r"stackoverflow\.com/questions/", re.IGNORECASE),
    re.compile(r"youtube\.com/watch", re.IGNORECASE),
    re.compile(r"(?:twitter|x)\.com/\w+/status/", re.IGNORECASE),
    re.compile(r"quora\.com/", re.IGNORECASE),
]


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        return parsed.hostname
    except Exception:
        return None


def is_hard_reject(url: str) -> bool:
    return any(p.search(url) for p in HARD_REJECT_PATTERNS)


def is_tier5_flag(url: str) -> bool:
    return any(p.search(url) for p in TIER5_FLAG_PATTERNS)


def classify_tier(url: str) -> int | None:
    """Map a URL's host to a credibility tier (1-3) via the positive allowlist.

    Suffix-aware exact/parent match against DOMAIN_TIER_MAP, then structural TLD
    suffixes. Returns None for an unrecognized host -- accepted but not counted toward
    the Tier 1-3 minimum (the gate enforces recognized quality, not merely 'not junk').
    """
    host = (extract_domain(url) or "").lower().lstrip(".")
    if not host:
        return None
    for d, tier in DOMAIN_TIER_MAP.items():
        if host == d or host.endswith("." + d):
            return tier
    for suffix, tier in SUFFIX_TIER_MAP:
        if host.endswith(suffix):
            return tier
    return None


def fetch_sources(notebook_id: str) -> list[dict]:
    try:
        result = subprocess.run(
            ["notebooklm", "source", "list", "--json", "--notebook", notebook_id],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"ERROR: notebooklm source list failed: {result.stderr.strip()}", file=sys.stderr)
            return []
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("sources", data.get("items", []))
        return []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: fetch_sources: {e}", file=sys.stderr)
        return []


def fetch_fulltext(notebook_id: str, source_id: str) -> str | None:
    try:
        result = subprocess.run(
            ["notebooklm", "source", "fulltext", source_id, "--json", "--notebook", notebook_id],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            return data.get("text", data.get("content", data.get("fulltext", "")))
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def check_markdown_provenance(notebook_id: str, source: dict) -> list[str]:
    flags: list[str] = []
    source_id = source.get("id", source.get("source_id", ""))
    title = source.get("title", "")

    if not source.get("url") and not source.get("web_url"):
        flags.append("no_url")
    if GENERIC_TITLE_RE.search(title):
        flags.append("generic_title")

    fulltext = fetch_fulltext(notebook_id, source_id)
    if fulltext is None:
        flags.append("fulltext_unavailable")
        return flags

    if len(fulltext) > 20000:
        flags.append("high_char_count")

    first_500 = fulltext[:500].lower()
    if not any(marker in first_500 for marker in ["author", "by ", "written by", "et al"]):
        flags.append("no_author")

    for pattern in HARD_REJECT_CONTENT_PATTERNS:
        if pattern.search(fulltext):
            domain_match = pattern.pattern.split(r"\.")[0].split(r"/")[-1]
            flags.append(f"references_{domain_match}")

    return flags


def classify_source(source: dict, notebook_id: str, check_markdown: bool = False) -> dict:
    source_id = source.get("id", source.get("source_id", ""))
    title = source.get("title", "")
    url = source.get("url", source.get("web_url", ""))
    source_type = source.get("type", source.get("source_type", "UNKNOWN")).upper()

    domain = extract_domain(url)
    flags: list[str] = []
    decision = "accept"
    tier = None

    if url and is_hard_reject(url):
        decision = "hard_reject"
        flags.append("hard_reject_domain")
    elif url and is_tier5_flag(url):
        tier = 5
        flags.append("tier5_domain")
    elif url:
        # Accepted source: assign a positive tier if the host is recognized.
        tier = classify_tier(url)
        if tier is None:
            flags.append("unclassified_domain")
    elif not url and source_type in ("MARKDOWN", "TEXT", "UNKNOWN"):
        flags.append("no_url")
        if check_markdown:
            md_flags = check_markdown_provenance(notebook_id, source)
            flags.extend(md_flags)
            if any(f.startswith("references_") for f in md_flags):
                decision = "hard_reject"
                flags.append("laundered_reference")

    return {
        "source_id": source_id,
        "title": title,
        "url": url or None,
        "source_type": source_type,
        "tier": tier,
        "domain": domain,
        "decision": decision,
        "flags": flags,
    }


def delete_source(notebook_id: str, source_id: str) -> bool:
    try:
        result = subprocess.run(
            ["notebooklm", "source", "delete", source_id, "--yes", "--notebook", notebook_id],
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def load_notebook_index(index_path: Path) -> tuple[list | dict, list[dict]]:
    if not index_path.is_file():
        return [], []
    try:
        data = json.loads(index_path.read_text())
    except (json.JSONDecodeError, OSError):
        return [], []
    if isinstance(data, list):
        return data, data
    if isinstance(data, dict):
        entries = data.get("notebooks", data.get("entries", []))
        if isinstance(entries, list):
            return data, entries
    return data, []


def update_notebook_index(notebook_id: str, audit_result: dict, index_path: Path) -> bool:
    raw_data, entries = load_notebook_index(index_path)
    for entry in entries:
        if isinstance(entry, dict) and entry.get("notebook_id") == notebook_id:
            entry["source_audit"] = audit_result
            break
    else:
        print(f"WARNING: notebook {notebook_id} not found in index, cannot record audit", file=sys.stderr)
        return False
    try:
        index_path.write_text(json.dumps(raw_data, indent=2) + "\n")
        return True
    except OSError as e:
        print(f"ERROR: writing notebook-index.json: {e}", file=sys.stderr)
        return False


def run_audit(notebook_id: str, index_path: Path, dry_run: bool = False,
              skip_delete: bool = False, check_markdown: bool = False) -> dict:
    print(f"Auditing notebook {notebook_id}...")
    sources = fetch_sources(notebook_id)
    if not sources:
        print("No sources found or fetch failed.")
        return {"completed": False, "error": "no_sources_or_fetch_failed"}

    print(f"Found {len(sources)} sources. Classifying...")

    per_source: list[dict] = []
    hard_rejects: list[dict] = []

    for s in sources:
        record = classify_source(s, notebook_id, check_markdown=check_markdown)
        per_source.append(record)
        if record["decision"] == "hard_reject":
            hard_rejects.append(record)

    print(f"Classification complete: {len(hard_rejects)} hard-reject(s) found.")

    deleted_count = 0
    if hard_rejects and not dry_run and not skip_delete:
        print(f"Deleting {len(hard_rejects)} hard-reject source(s)...")
        for i, reject in enumerate(hard_rejects):
            sid = reject["source_id"]
            print(f"  [{i+1}/{len(hard_rejects)}] Deleting {sid} ({reject['title'][:60]})")
            if delete_source(notebook_id, sid):
                reject["decision"] = "hard_reject_deleted"
                deleted_count += 1
            else:
                reject["decision"] = "hard_reject_delete_failed"
                print(f"    FAILED to delete {sid}", file=sys.stderr)
            if i < len(hard_rejects) - 1:
                time.sleep(2.5)
    elif hard_rejects and dry_run:
        print("DRY RUN: would delete:")
        for r in hard_rejects:
            print(f"  - {r['source_id']}: {r['title'][:60]} ({r['domain']})")

    tier_dist = {"tier_1": 0, "tier_2": 0, "tier_3": 0, "tier_4": 0,
                 "tier_5_excluded": 0, "unclassified": 0}
    for r in per_source:
        if r["decision"] in ("hard_reject", "hard_reject_deleted") or r.get("tier") == 5:
            tier_dist["tier_5_excluded"] += 1
        elif r.get("tier") in (1, 2, 3, 4):
            tier_dist[f"tier_{r['tier']}"] += 1
        else:
            tier_dist["unclassified"] += 1

    md_flagged = sum(
        1 for r in per_source
        if "no_url" in r.get("flags", []) and any(f.startswith("references_") for f in r.get("flags", []))
    )

    effective_tier_1_3 = tier_dist["tier_1"] + tier_dist["tier_2"] + tier_dist["tier_3"]

    audit_result = {
        "completed": True,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "auditor": f"research-qa-source-audit v{VERSION}",
        "total_sources": len(sources),
        "hard_rejects_found": len(hard_rejects),
        "hard_rejects_deleted": deleted_count,
        "markdown_provenance_checked": check_markdown,
        "markdown_flagged": md_flagged,
        "tier_distribution": tier_dist,
        "unclassified_count": tier_dist["unclassified"],
        "effective_tier_1_3": effective_tier_1_3,
        "per_source": per_source,
    }

    print(f"\nAudit summary:")
    print(f"  Total sources: {len(sources)}")
    print(f"  Hard rejects found: {len(hard_rejects)}")
    print(f"  Hard rejects deleted: {deleted_count}")
    print(f"  Tier distribution: T1={tier_dist['tier_1']} T2={tier_dist['tier_2']} "
          f"T3={tier_dist['tier_3']} T4={tier_dist['tier_4']} "
          f"T5/rejected={tier_dist['tier_5_excluded']} unclassified={tier_dist['unclassified']}")
    print(f"  Effective Tier 1-3 (counts toward the >=15 minimum): {effective_tier_1_3}  "
          + ("PASS" if effective_tier_1_3 >= 15
             else "below the 15 Tier 1-3 minimum in SOURCE-QUALITY.md (advisory, non-blocking)"))
    if tier_dist["unclassified"]:
        print(f"  Unclassified accepted domains (not counted): {tier_dist['unclassified']} "
              f"-- if any are legitimate, add them to DOMAIN_TIER_MAP")

    if not dry_run:
        if update_notebook_index(notebook_id, audit_result, index_path):
            print(f"  Recorded to notebook-index.json")
        else:
            print(f"  WARNING: Failed to record to notebook-index.json", file=sys.stderr)

    return audit_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Research agent source audit")
    parser.add_argument("--notebook", required=True, help="NotebookLM notebook ID")
    parser.add_argument("--dry-run", action="store_true", help="Classify only, no deletions or index updates")
    parser.add_argument("--skip-delete", action="store_true", help="Classify and record, but skip deletions")
    parser.add_argument("--check-markdown", action="store_true", help="Check MARKDOWN source provenance via fulltext")
    parser.add_argument("--index-path", type=Path, default=None,
                        help="Path to notebook-index.json (default: ~/research-agent/observability/notebook-index.json)")
    args = parser.parse_args()

    index_path = args.index_path or Path(os.environ.get("NOTEBOOK_INDEX_PATH", str(DEFAULT_INDEX_PATH)))

    result = run_audit(
        notebook_id=args.notebook,
        index_path=index_path,
        dry_run=args.dry_run,
        skip_delete=args.skip_delete,
        check_markdown=args.check_markdown,
    )
    sys.exit(0 if result.get("completed") else 1)


if __name__ == "__main__":
    main()
