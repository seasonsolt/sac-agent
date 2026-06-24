# DeepAgent Flow

SAC Agent already depends on LangChain and DeepAgent, but the current runner
does not call a model. That is deliberate. The repository teaches the runtime
shape first: session state, tool boundaries, approval, and patch application.

## Why The Runner Is Deterministic

The tests need stable behavior. A live model would add several sources of
change:

- API keys must be configured.
- Network calls can fail.
- Model responses can vary.
- Prompt changes can alter tool choices.
- Tool execution can become harder to test.

The current `DeepAgentRunner.run_turn()` records a message, records a planning
event, and returns a fixed response. That makes CI reliable and lets learners
inspect the runtime without debugging model behavior at the same time.

## Intended Integration Point

`src/sac_agent/agent/runner.py` is the integration point for a future
LangChain/DeepAgent loop. It already owns:

- the system prompt from `agent/prompts.py`
- the controlled `ToolRegistry`
- the session object for messages and runtime events

A future implementation can build a DeepAgent instance inside the runner and
adapt registry tools into the format DeepAgent expects.

## Expected Future Flow

A model-backed turn should keep this shape:

```text
TUI receives user input
  -> runner records the user message
  -> runner calls DeepAgent with prompt, history, and available tools
  -> DeepAgent asks for a tool
  -> registry resolves the tool by name
  -> tool records events and returns structured data
  -> risky commands or patches create approval requests
  -> TUI asks the human to approve or reject
  -> approved writes run through the guarded primitive
  -> runner records the final answer
```

The model should propose actions. It should not directly mutate the repository,
spawn arbitrary subprocesses, or write files outside the patch workflow.

## Tool Adapter Notes

The registry currently stores Python callables. A DeepAgent adapter can expose
each registered tool with:

- name
- description
- argument schema
- callable wrapper

The wrapper should translate tool results into plain structured values and
record `RuntimeEvent` entries on the session. Avoid letting the model see raw
Python exceptions as its only feedback. Turn expected failures into clear tool
results where possible.

## Approval Notes

DeepAgent may decide that a risky command or patch is needed. The runtime
should pause at that point and request approval. The model should not be able
to mark its own request as approved.

For teaching, this makes the trust boundary visible:

```text
model proposes -> runtime classifies -> human decides -> runtime executes
```

## What Is Not Implemented Yet

The repository does not yet include:

- a live model client
- a DeepAgent tool adapter
- a full planning loop
- a TUI approval dialog
- automatic patch generation from a model response

Those pieces should be added after the existing deterministic skeleton remains
well tested.
