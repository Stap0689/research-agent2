# NotebookLM Integration Reference

## CLI Commands by Phase

### Authentication
```bash
notebooklm auth check                    # Quick local validation
notebooklm auth check --test             # Full validation with network test
```

### Phase 1: Notebook Creation
```bash
notebooklm create "Research: [Topic]" --json    # Returns notebook ID
notebooklm list --json                           # List existing notebooks
notebooklm use <notebook-id>                     # Set active context (single-agent only)
```

### Phase 1-2: Source Collection
```bash
# Primary method — deep web research
notebooklm source add-research "query terms" --mode deep --notebook <ID>

# Wait and import all found sources (ALWAYS use --timeout 600+ for deep research)
notebooklm research wait --import-all --timeout 600 --notebook <ID>

# Check status without blocking
notebooklm research status --notebook <ID>

# Non-blocking start, monitor separately
notebooklm source add-research "query" --mode deep --no-wait --notebook <ID>
notebooklm research wait --import-all --notebook <ID>

# Add a specific URL directly
notebooklm source add "https://example.com" --notebook <ID>

# Add a local file
notebooklm source add ./path/to/file.md --notebook <ID>

# List all sources
notebooklm source list --notebook <ID> --json
```

### Phase 3-4: Q&A
```bash
# Ask and save response as note (required — never skip --save-as-note)
notebooklm ask "Your question" --save-as-note --notebook <ID>

# Ask using specific sources only
notebooklm ask "Question" -s <source_id> -s <source_id> --save-as-note --notebook <ID>

# List all saved notes
notebooklm note list --notebook <ID>
```

### Parallel Workflow Safety
When running multiple agents against different notebooks, always use explicit `--notebook <ID>` flags. Never rely on `notebooklm use` in multi-agent contexts — it writes to a shared context file and agents will overwrite each other.

---

## Rate Limit and Timeout Handling

**Critical distinction:** a `research wait` RPC timeout is NOT the same as an import failure. Partial imports frequently succeed even when the wait command times out. Never treat a timeout as fatal without checking what actually imported.

### `research wait --import-all` Timeout Recovery (RPC Timeout Pattern)
This timeout pattern is consistent across notebooks when deep research takes longer than the wait window.

```bash
# Step 1: timeout occurs on research wait --import-all
# Step 2: IMMEDIATELY check what actually imported — do not stop or retry blindly
notebooklm source list --json --notebook <ID>
```

**Decision based on source list:**

**Sources present (even partial):**
Proceed. Run the source audit on what imported. Note the partial import in the decision record under Intelligence Gaps. Continue to the next research query.

**Zero sources imported:**
Do not escalate immediately. First attempt manual recovery:
```bash
# Add qualifying sources directly — use specific, high-quality URLs relevant to the query
notebooklm source add "https://specific-quality-source-url.com" --notebook <ID>
notebooklm source add "https://another-quality-source.com" --notebook <ID>
# Repeat for 3-5 targeted sources that cover what the failed query was meant to find
```
After manual additions, run the source audit as normal. Document that the research query timed out with zero import and that sources were added manually — note this in the decision record as a corpus limitation.
If no suitable manual sources can be identified: escalate to user with corpus state.

**Sources in `processing` state:**
Wait 60 seconds, recheck. Processing sources complete independently of the wait command — they are not lost.

Do not retry `research wait --import-all` in a loop after a timeout — it will not recover more sources. The import either happened or it didn't. Check the list and move on.

### ⚠️ Deep Research Import Duplication Bug

`research wait --import-all` with short timeouts triggers a retry loop where each retry re-imports the full result set. A single query returning 71 sources can produce 378 sources (5.3x duplication) if 5 retries fire.

**Root cause:** The CLI's retry mechanism does not track which sources were already imported. Each retry attempt imports the complete batch again.

**Prevention:**
1. **Always use `--timeout 600` or higher** for deep research to avoid triggering retries
2. **Record source count before and after** every `research wait --import-all`
3. If post-import count is 2x+ the expected delta, run emergency dedup before proceeding

**Detection:** After every import, compare pre/post source counts. If DELTA > 80 from a single query, duplication has occurred.

**Cleanup cost:** Source deletion runs at ~2.3s per source. Cleaning 220 duplicates takes ~8.5 minutes. Prevention is always cheaper.

See the ⛔ IMPORT DEDUP GUARD section in SKILL.md for the full protocol.

### Rate Limit Failures (Query Won't Start)

| Symptom | Action |
|---------|--------|
| `source add-research` fails immediately with quota/limit error | Subscription ceiling — stop and escalate to user (see SKILL.md) |
| `source add-research` fails with timeout or transient error | Wait 2 minutes, retry once |
| Still failing after retry | Wait 5 minutes, retry once more |
| Still failing after 5 minutes + 0 sources loaded | Escalate to user with corpus state |
| Still failing after 5 minutes + 15+ Tier 1–3 sources loaded | Proceed to Q&A, document the failed query as an Intelligence Gap |

**Never run multiple deep research queries in parallel on the same notebook.** Sequence them and wait for each to complete.

---

## Note-Saving Conventions

- **All Q&A responses must be saved with `--save-as-note`** — never rely on terminal output alone
- The Phase 4 synthesis question must be saved as a note
- Notes become the documented evidence trail for the deliverable
- Session context is lost if the connection drops — notes are permanent
- If a note save fails, retry the question immediately before continuing

---

## Source Processing Timelines

| Source Type | Typical Processing Time |
|-------------|------------------------|
| Web page | 10–30 seconds |
| PDF (small, <50 pages) | 30–90 seconds |
| PDF (large, 50+ pages) | 2–5 minutes |
| Deep research import (20+ sources) | 2–10 minutes |
| Markdown file | 10–20 seconds |

Wait for sources to reach `status: ready` before running Q&A. A source in `processing` state will return incomplete answers.

```bash
# Check source status
notebooklm source list --notebook <ID> --json | grep -E '"status"'
```

---

## Troubleshooting

**"No notebook context" error:**
Use `--notebook <ID>` explicitly on every command. Do not rely on `notebooklm use` in automated or multi-agent workflows.

**Q&A returns thin or generic answers:**
- Verify sources are in `ready` state before asking
- Check source count — fewer than 20 sources usually produces weak answers
- Reframe the question using Round 3 (falsification) framing — NotebookLM responds better to specific, falsifiable questions than broad ones

**Research import shows 0 sources:**
- The query may have been too narrow or too technical for web search
- Broaden the query terms and retry
- Add specific high-quality sources manually with `source add <URL>`

**Auth errors mid-session:**
```bash
notebooklm auth check --test    # Diagnose
notebooklm login                 # Re-authenticate if needed
```
