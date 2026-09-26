# Installing research-agent2 on native Windows

This guide is for installing research-agent2 on **native Windows** (PowerShell, no
WSL). The main `README.md` and `observer/README.md` are written Unix-first (`cp -r`,
`chmod +x`, shebang-invoked hooks). None of that works as-written on Windows, but
**none of the Python needs to change** to run here. The runtime resolves all paths
with `Path.home()` and environment variables, and the hooks read `stdin`, so the
code is already cross-platform. Only the install steps and the hook wiring differ.

If you are an AI agent executing this install: follow the steps in order, run the
verification commands, and read the "Do not do these" section before touching
anything. Substitute the real absolute paths reported by the commands. Do not
reintroduce `chmod`, and do not assume a shebang will run the hooks.

---

## 0. Assumptions

- Windows 10/11 with PowerShell.
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and working on Windows.
- The `research-agent2` repo is already cloned locally. This guide calls that folder `$REPO`.
- A local browser (Chrome or Edge) signed in to the Google account that has NotebookLM / Gemini Notebook access.

Set a variable for the repo path so the copy commands are unambiguous (adjust to where you cloned it):

```powershell
$REPO = "C:\Users\steve\code\research-agent2"
```

---

## 1. Python 3.10+ and notebooklm-py

Confirm Python is on PATH and is 3.10 or newer:

```powershell
python --version
```

If `python` is not found, install Python 3.10+ from python.org and tick **"Add
python.exe to PATH"** during setup, or use the `py -3` launcher in place of
`python` everywhere below.

Install the dependency (the exact version research-agent2 targets):

```powershell
python -m pip install --upgrade pip
python -m pip install "notebooklm-py==0.8.2"
notebooklm --version
```

`notebooklm-py` 0.8.2 is the public PyPI package and it ships every subcommand this
skill uses (`ask`, `source search`, `source add-research`, `configure --persona`,
`research wait --task-id`, the `download`/`generate` families). No forked or private
build is required.

---

## 2. Authenticate NotebookLM

Native Windows is the easy case here: your browser is local, so cookie auth just
works. Run:

```powershell
notebooklm login
```

If it does not auto-detect your browser, point it at one explicitly:

```powershell
notebooklm login --browser-cookies chrome
# or
notebooklm login --browser msedge
```

Verify:

```powershell
notebooklm auth check --test
```

(The `--master-token` flow is only needed inside WSL where there is no local
browser. On native Windows you should not need it.)

---

## 3. Install the two skills

Claude Code on Windows reads skills from `%USERPROFILE%\.claude\skills`. Copy both
skill folders there:

```powershell
$SKILLS = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path "$SKILLS\research-agent2" | Out-Null
New-Item -ItemType Directory -Force -Path "$SKILLS\notebooklm"      | Out-Null

Copy-Item -Recurse -Force "$REPO\research-agent2\*" "$SKILLS\research-agent2\"
Copy-Item -Recurse -Force "$REPO\notebooklm\*"      "$SKILLS\notebooklm\"
```

Confirm `critical-core.json` landed (the hooks look for it here by default):

```powershell
Test-Path "$SKILLS\research-agent2\critical-core.json"   # must print True
```

---

## 4. Place the observer runtime

Pick a workspace root. The runtime defaults to `%USERPROFILE%\research-agent` when
`RESEARCH_AGENT_HOME` is unset, and `Path.home()` resolves to `%USERPROFILE%` on
Windows, so you can accept the default and skip setting any environment variable.

```powershell
$RAHOME = "$env:USERPROFILE\research-agent"
New-Item -ItemType Directory -Force -Path "$RAHOME\observer\hooks" | Out-Null
New-Item -ItemType Directory -Force -Path "$RAHOME\observability"  | Out-Null
New-Item -ItemType Directory -Force -Path "$RAHOME\findings"       | Out-Null

Copy-Item -Force "$REPO\observer\witness.py"   "$RAHOME\observer\"
Copy-Item -Force "$REPO\observer\hooks\*.py"   "$RAHOME\observer\hooks\"
```

There is **no `chmod` step**. Windows has no executable bit, and the hooks are
invoked explicitly through `python` in the next step, so file permissions are
irrelevant.

Optional: if you want a workspace root somewhere other than
`%USERPROFILE%\research-agent`, set it as a user environment variable so both Claude
Code and the hooks resolve the same place:

```powershell
[Environment]::SetEnvironmentVariable("RESEARCH_AGENT_HOME", "D:\research-agent", "User")
```

Then restart Claude Code so it inherits the variable.

---

## 5. Wire the three hooks (the important part)

On Unix these hooks run via their shebang. **Windows does not honor the shebang**, so
you must invoke each one through the Python interpreter explicitly. In
`%USERPROFILE%\.claude\settings.json`, each hook `command` is
`python <absolute-path-to-hook>` rather than the bare path.

Use forward slashes in the paths (Python on Windows accepts them and it avoids
JSON backslash-escaping mistakes). Replace `C:/Users/steve` with the real profile
path. If your user profile path contains a space, wrap the script path in escaped
quotes: `"python \"C:/Users/Steve Smith/research-agent/...\""`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python C:/Users/steve/research-agent/observer/hooks/witness-gate.py", "timeout": 5 }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python C:/Users/steve/research-agent/observer/hooks/completeness-gate.py", "timeout": 5 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python C:/Users/steve/research-agent/observer/hooks/witness-reinject.py", "timeout": 5 }
        ]
      }
    ]
  }
}
```

Notes:
- If `python` is not on PATH but the `py` launcher is, use `py -3 C:/Users/...`
  instead. Do not mix: pick whichever `--version` check in step 1 worked.
- The `Bash` matcher is correct on Windows. Claude Code names its shell tool `Bash`
  on every platform, so `witness-gate.py` and `witness-reinject.py` still fire on
  `notebooklm ask` calls.
- If you already have a `hooks` block in `settings.json`, merge these entries into
  the existing `PreToolUse` / `PostToolUse` arrays rather than overwriting them.

Restart Claude Code after editing `settings.json`.

---

## 6. Verify the install

Run each hook manually to confirm Python can execute it and it fails open on empty
input (an allow decision, exit 0, no crash):

```powershell
'{}' | python "$env:USERPROFILE\research-agent\observer\hooks\witness-gate.py"; echo "exit=$LASTEXITCODE"
'{}' | python "$env:USERPROFILE\research-agent\observer\hooks\completeness-gate.py"; echo "exit=$LASTEXITCODE"
'{}' | python "$env:USERPROFILE\research-agent\observer\hooks\witness-reinject.py"; echo "exit=$LASTEXITCODE"
```

Each should exit 0 and not throw. Then confirm the state hub runs:

```powershell
python "$env:USERPROFILE\research-agent\observer\witness.py" gotcha-list
```

Finally, in a Claude Code session, start a research task with the observer model
(for example: "Research X using the observer model, accuracy is critical"). The
first `notebooklm ask` should be gated until the methodology is confirmed read,
which proves the hook is firing.

---

## Do not do these (common wrong "fixes")

An agent adapting Unix instructions tends to break the install in these specific
ways. Avoid them:

- **Do not add `chmod +x`.** It does nothing useful on Windows and may error. The
  hooks run via explicit `python`, not an exec bit.
- **Do not write the hook `command` as a bare path** (e.g.
  `"command": "C:/.../witness-gate.py"`). Windows will not run it through the
  shebang. It must be `python <path>` or `py -3 <path>`.
- **Do not edit the Python source** to "make it Windows-compatible." It already is.
  `Path.home()`, `os.environ`, and `sys.stdin` are cross-platform. Changing paths in
  the code will desync it from the defaults the skill and docs assume.
- **Do not use the `--master-token` login flow** unless the plain `notebooklm login`
  and `--browser-cookies` options both fail. On native Windows the local browser
  cookie path is the normal one.
- **Do not overwrite an existing `settings.json` `hooks` block.** Merge into it.

---

## If native Windows fights you: WSL is the clean fallback

Everything above is a native-Windows adaptation of a Unix-first project. If you hit
friction that is not worth debugging (usually a PATH or `settings.json` shell issue),
install WSL2 + Ubuntu, run Claude Code and Python inside it, and follow the main
`README.md` and `observer/README.md` verbatim. The one WSL cost is authentication:
inside WSL there is no local browser, so use `notebooklm login --master-token`
instead of cookie auth. That is the only difference from the documented Unix path.
