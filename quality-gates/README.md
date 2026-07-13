# Quality Gates

Source quality enforcement for the research-agent methodology. Ensures hard-reject sources (per SOURCE-QUALITY.md) are identified and deleted before Q&A rounds begin.

## Why

Documentation alone does not prevent agents from skipping quality requirements. In production, 68 hard-reject sources (Reddit, StackOverflow, YouTube) survived into research corpora across 12 notebooks. This tooling makes source auditing structural, not advisory.

## source-audit.py

Standalone CLI that fetches sources from a NotebookLM notebook, classifies them against the SOURCE-QUALITY.md tier hierarchy, auto-deletes hard-reject sources, and records a per-source audit trail in notebook-index.json.

```bash
# Classify and delete hard-rejects
source-audit.py --notebook <ID>

# Dry run (no deletions, no index updates)
source-audit.py --notebook <ID> --dry-run

# Include MARKDOWN provenance checking (scans uploaded content for laundered references)
source-audit.py --notebook <ID> --check-markdown

# Custom notebook-index.json path
source-audit.py --notebook <ID> --index-path ./my-index.json
```

### What it does

1. Fetches `notebooklm source list --json` for the target notebook
2. Domain-matches each source against hard-reject patterns
3. Flags Tier 5 borderline domains
4. Optionally scans MARKDOWN source content for laundered hard-reject references
5. Deletes hard-reject sources (with rate-limit-safe 2.5s spacing)
6. Records per-source classification to notebook-index.json

### MARKDOWN provenance (`--check-markdown`)

Uploaded MARKDOWN sources bypass URL-based domain matching. The `--check-markdown` flag retrieves source fulltext and scans for hard-reject domain references embedded in bibliographies or citations. This catches laundering patterns where a fabricated document cites Reddit/StackOverflow posts as references.

## Hard-Reject Domains

Rejected with no exceptions (per SOURCE-QUALITY.md):

- Reddit, StackOverflow, StackExchange
- GeeksforGeeks, Scribd
- YouTube, TikTok
- LinkedIn posts/pulse, Twitter/X
- Quora, Emergent Mind

## persona-guard.py

PreToolUse hook that prevents accidental custom persona destruction.

**Problem:** `notebooklm configure --response-length longer` (without `--persona`) silently resets the chat goal from CUSTOM to DEFAULT, destroying the custom persona. Similarly, `--mode` switches override custom persona without warning. This is a bug in notebooklm-py <= 0.3.4 where `configure()` defaults to `ChatGoal.DEFAULT` when no explicit goal is provided, regardless of what's currently set on the server.

**What it blocks:**
- `notebooklm configure --response-length <value>` without `--persona`
- `notebooklm configure --mode <value>` (warns that it will destroy custom persona)

**What it allows:**
- `notebooklm configure --persona "..." --response-length <value>` (safe)
- `notebooklm configure --persona "..."` (safe)
- Any non-configure notebooklm commands

**Bypass:** `PERSONA_GUARD_OVERRIDE=1`

```bash
# Install as Claude Code PreToolUse hook (settings.json)
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/quality-gates/persona-guard.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Claude Code Integration

For Claude Code users: a PreToolUse hook can block `notebooklm ask` commands unless the source audit has been completed and persona is configured. See the gate pattern in the Claude Code hooks documentation. The audit script writes the state that such a gate reads, keeping the gate fast (file read only, no network calls).

## Configuration

Set `NOTEBOOK_INDEX_PATH` env var to override the default notebook-index.json location.
