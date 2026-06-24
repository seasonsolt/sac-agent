# SAC Agent

SAC Agent is a teaching-oriented personal Software Engineer Agent. It is a
small Python project that shows how a coding agent can organize a session,
inspect a repository, classify tools, ask for approval, and apply patches
through a narrow write path.

SAC Agent is not related to the open-source `swe-agent` project. The package
name is `sac-agent`, and the installed terminal command is `sac`.

## Current Status

This repository currently contains a deterministic teaching skeleton:

- A Typer CLI starts the Textual TUI with `sac [repo]`.
- The runner records a user message and a planning event without calling a live
  model.
- Repository tools are read-only, except for the explicit patch application
  primitive.
- Shell commands pass through a risk classifier before execution.
- The project includes LangChain and DeepAgent dependencies so the future
  model-backed path has a clear place to attach.

Model-backed execution is intentionally a later extension. The deterministic
runner keeps tests and CI independent of API keys, network access, model
availability, and prompt drift.

## Installation From Source

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/seasonsolt/sac-agent.git
cd sac-agent
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

After installation, the CLI entry point is:

```bash
sac [repo]
```

If you omit `[repo]`, SAC Agent opens the current directory.

During local development you can also run the module through the virtual
environment:

```bash
.venv/bin/sac .
```

## Development Checks

Run tests from the local virtual environment:

```bash
.venv/bin/python -m pytest -q
```

Run Ruff from the same environment:

```bash
.venv/bin/python -m ruff check .
```

## Project Layout

```text
src/sac_agent/
  cli.py                 Typer entry point for the `sac` command.
  agent/
    prompts.py           System prompt text for the future model-backed runner.
    runner.py            Deterministic runner used by the TUI and tests.
  runtime/
    approvals.py         Approval request and decision models.
    commands.py          Shell command risk classifier.
    events.py            Session event records shown in the TUI.
    patches.py           Patch proposal parsing and `git apply` wrapper.
    session.py           Session state, message history, and repo validation.
  tools/
    registry.py          Controlled list of tools exposed to the runner.
    repo.py              Read-only repository inspection helpers.
    shell.py             Guarded shell command execution.
  tui/
    app.py               Textual user interface.

tests/                   Focused tests for runtime boundaries and tools.
docs/                    Teaching notes for architecture, safety, and flow.
```

## Safety Model

SAC Agent treats the model, future tools, and shell as separate trust zones.
The current code is small, but it keeps the same boundaries a larger agent
would need:

- Read-only repository tools list files, read UTF-8 files, and inspect
  `git status`.
- The repo path guard resolves selected paths and rejects parent-directory,
  absolute-path, and symlink escapes.
- The command classifier marks known read-only commands as safe and treats
  mutating, networked, empty, or unknown commands as risky.
- The shell tool blocks risky commands unless the caller explicitly opts in
  with `allow_risky=True`. Connecting that opt-in to `ApprovalGate` and the TUI
  is future integration work.
- Patch proposals can summarize changed files. The intended controller/TUI flow
  should call `apply_patch()` only after approval; `apply_patch()` is the narrow
  `git apply --whitespace=fix` write primitive, not an approval-enforcing
  primitive.
- The approval gate keeps pending requests and human decisions separate from
  tool code.

Chinese note: 这个项目的重点是学习边界设计。模型以后可以更聪明，但不应该绕过这些安全边界。

## Publishing Target

The intended public repository name is `sac-agent`. The Python package name is
`sac-agent`, and the user-facing command is `sac`.

## Further Reading

- [Architecture](docs/architecture.md)
- [DeepAgent Flow](docs/deepagent-flow.md)
- [Approval and Safety](docs/approval-and-safety.md)
- [Walkthrough](docs/walkthrough.md)
