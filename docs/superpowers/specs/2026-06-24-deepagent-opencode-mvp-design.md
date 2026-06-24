# DeepAgent Opencode MVP Design

## Goal

SAC Agent should become a fast, minimally usable SWE coding CLI. The product direction is closer to opencode than the current teaching TUI: the terminal should center on a readable coding conversation, with tool calls, command output, and safety decisions shown inline.

DeepAgent should be used as the MVP agent core because it is already installed and provides a ready tool-calling coding-agent loop. SAC should still own the TUI, session event model, repository boundary, command classification, and approval policy.

## Scope

The MVP should provide:

- An opencode-style single conversation stream.
- Inline tool/event cards for model activity, shell commands, file reads, and blocked risky actions.
- A runner boundary that can use DeepAgent when a model is configured.
- A deterministic fallback runner when no model is configured, so tests and local demos do not require API keys.
- A compact status surface showing repository path and latest runtime state.

The MVP should not provide:

- A full IDE file browser.
- Multi-agent orchestration beyond what DeepAgent may use internally.
- Automatic risky shell execution.
- A complete patch approval workflow.
- A custom agent loop from scratch.

## Architecture

`SacTuiApp` remains the terminal UI owner. It renders a main conversation log, a compact status panel, and a bottom prompt input. It does not import DeepAgent or call tools directly.

`DeepAgentRunner` remains the runtime boundary. It records the user message, chooses a backend path, invokes the agent or fallback command router, and records `RuntimeEvent` entries for every visible action.

The runner has two modes:

- `deepagent`: enabled when a model name or model object is configured.
- `fallback`: enabled by default for tests and no-key local usage.

The fallback mode should still be useful. It supports direct commands such as `status`, `files`, `read <path>`, and `run <argv...>` through the existing `ToolRegistry`.

DeepAgent mode should create the agent lazily, convert SAC tools into LangChain-compatible tools where needed, and stream or collect events into SAC runtime events. Built-in DeepAgent file and shell tools may be used only when permissions or interrupts preserve SAC's safety defaults.

## Safety

SAC safety defaults are stricter than a generic agent framework:

- Repository access must stay rooted at `AgentSession.repo_path`.
- Risky shell commands remain blocked unless explicit approval is later added.
- The first DeepAgent MVP should prefer read-only and low-risk shell behavior.
- Any tool failure should be displayed as data in the conversation rather than crashing the TUI.

DeepAgent is an execution engine, not the safety source of truth.

## TUI Behavior

The main log should show entries in this order for each turn:

- User prompt.
- Assistant response or status.
- Tool cards, including tool name, arguments summary, result status, and short output.
- Error or blocked-action cards when applicable.

The status panel should show:

- Open repository.
- Runner mode.
- Latest event kind.
- Pending approval state, initially always none.

The input remains the main interaction point. Users should not need to learn slash commands for the MVP, but direct fallback commands should work for fast local validation.

## Testing

Tests should cover:

- Fallback runner command routing for status, files, read, and shell command execution.
- Blocked risky shell command behavior.
- DeepAgent dependency availability and lazy construction boundary.
- TUI widget structure for the new conversation/status layout.
- Markup escaping for user text, agent text, and event text.

The test suite must pass without live model credentials.

## Open Decisions

The first implementation should use fallback mode by default and add configuration for DeepAgent mode without requiring it in tests. The exact model environment variable can be simple at first, such as `SAC_MODEL`, with provider-specific credentials delegated to LangChain provider packages.
