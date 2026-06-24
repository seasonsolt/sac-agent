# Architecture

SAC Agent is a small teaching project for a personal Software Engineer Agent.
The current implementation favors explicit runtime boundaries over model
features. That makes the code useful for learning and keeps the test suite
deterministic.

## Entry Point

`src/sac_agent/cli.py` defines the Typer app and installs the `sac` command
through `pyproject.toml`.

```bash
sac [repo]
```

The optional `repo` argument defaults to the current directory. The CLI expands
and resolves the path before creating the TUI.

## TUI Layer

`src/sac_agent/tui/app.py` owns the Textual interface:

- The left pane shows chat messages.
- The right pane shows recent runtime events.
- The input box sends each submitted command to the runner.

The TUI creates one `AgentSession` and one `DeepAgentRunner` when the app
starts. The TUI should remain the place where a human sees future approval
requests and makes decisions.

## Session Layer

`src/sac_agent/runtime/session.py` stores session state:

- `session_id`
- resolved `repo_path`
- chat messages
- runtime events
- a future pending patch field
- verification results

`AgentSession.start()` validates that the repository path exists and is a
directory. The rest of the runtime should use this resolved path instead of
accepting arbitrary paths from a model or a tool call.

## Runner Layer

`src/sac_agent/agent/runner.py` contains `DeepAgentRunner`. The class name
points at the intended LangChain/DeepAgent direction, but the current
`run_turn()` method is deterministic:

1. Record the user message.
2. Record an agent planning event.
3. Return a fixed teaching response.

This keeps tests independent of API keys, network access, and model output.
The runner is the right place to add a future model-backed loop because it
already receives the session and a controlled tool registry.

## Runtime Boundary Modules

`src/sac_agent/runtime/approvals.py` defines approval request and decision
models. The approval gate tracks pending requests separately from decisions so
tool code can ask for permission without granting it.

`src/sac_agent/runtime/commands.py` classifies shell commands as `safe` or
`risky`. The classifier is conservative: unknown commands are risky.

`src/sac_agent/runtime/patches.py` models patch proposals, extracts changed
files from git diffs for display, and applies accepted diffs through
`git apply --whitespace=fix`.

`src/sac_agent/runtime/events.py` defines event records shown in the activity
pane. These events are a teaching surface because they let a learner connect
agent behavior with runtime actions.

## Tool Layer

`src/sac_agent/tools/repo.py` contains read-only repository helpers:

- `list_files()`
- `read_file()`
- `git_status()`

`read_file()` uses a repo path guard so a relative path cannot escape the
selected repository.

`src/sac_agent/tools/shell.py` contains the guarded shell runner. It asks
`classify_command()` for a risk decision before calling `subprocess.run()`.

`src/sac_agent/tools/registry.py` exposes tools through a single registry.
Future model-backed execution should call tools from this registry instead of
importing helpers directly.

## Data Flow

The current deterministic flow is:

```text
User input
  -> Textual TUI
  -> AgentSession.record_user_message()
  -> DeepAgentRunner.run_turn()
  -> AgentSession.record_event()
  -> Textual chat and activity logs
```

A future model-backed flow should preserve the same safety boundaries:

```text
User input
  -> TUI
  -> AgentSession
  -> DeepAgentRunner
  -> ToolRegistry
  -> repo tools / shell guard / approval gate / patch workflow
  -> AgentSession events
  -> TUI
```

Chinese note: 先把数据流画清楚，再接模型。这样调试时你知道每一步是谁负责的。
