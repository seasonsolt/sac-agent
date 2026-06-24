# Walkthrough

This walkthrough follows the code that exists today and points out where the
future patch approval flow will connect.

## 1. Install The Project

From a local clone:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

## 2. Launch The TUI

Open a repository:

```bash
.venv/bin/sac /path/to/repo
```

Or open the current directory:

```bash
.venv/bin/sac .
```

The CLI comes from `src/sac_agent/cli.py`. It resolves the repository path and
starts `SacTuiApp`.

## 3. Submit A Message

Type a request into the input box, for example:

```text
Add a README section explaining tests.
```

The TUI sends that string to `DeepAgentRunner.run_turn()`.

## 4. Watch The Session State

The runner records the user message on `AgentSession.messages`. It also records
runtime events on `AgentSession.events`.

The activity pane shows recent events so you can see what the runtime did. In
the deterministic skeleton, the runner records a planning event and returns a
fixed response.

## 5. Inspect Tools

The runner owns a `ToolRegistry`. The default registry exposes:

- `git_status`
- `list_files`
- `read_file`
- `run_shell_command`

The current runner does not call these tools yet. A future model-backed runner
should call tools through the registry so tool review stays in one place.

## 6. Understand A Safe Read

When a future runner calls `read_file(repo_path, "src/app.py")`, the repo tool:

1. resolves the repository path
2. resolves the selected file path
3. rejects the request if the selected path escapes the repo
4. reads UTF-8 text and returns the requested line range

This teaches an important agent rule: even read tools need path boundaries.

## 7. Understand A Guarded Shell Command

When a future runner calls `run_shell_command(repo_path, argv)`, the shell tool:

1. classifies the command
2. blocks risky commands unless approval has already been granted
3. runs approved or safe commands in the repository directory
4. returns stdout, stderr, and return code as structured data

For example, `rg AgentSession` is safe. `pip install requests` is risky because
it can change the environment and use the network.

## 8. Future Patch Approval Flow

The intended patch path is:

```text
model proposes a diff
  -> runtime builds PatchProposal(summary, diff)
  -> UI shows summary, changed files, and diff
  -> ApprovalGate records the pending request
  -> human approves or rejects
  -> accepted diff runs through apply_patch()
  -> verification commands run
  -> session records the result
```

The current code already has `PatchProposal`, changed-file parsing, and
`apply_patch()`. The TUI approval dialog and model-generated patches are future
work.

## 9. Run Verification

After code or docs changes, run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
```

These commands are the local checks used by this teaching skeleton.
