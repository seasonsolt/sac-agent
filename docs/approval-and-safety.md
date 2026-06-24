# Approval And Safety

SAC Agent keeps risky work behind narrow runtime boundaries. The code is small,
but the safety model is the same one a model-backed coding agent needs.

## Command Classification

`src/sac_agent/runtime/commands.py` classifies commands before the shell tool
runs them.

Allowed commands are low-risk inspection commands plus the project test runner:

- `git status`
- `git diff`
- `git log`
- `git show`
- `ls`
- `rg`
- `pytest`

`pytest` is not read-only. It executes repository code and may mutate files or
use network access, depending on the tests. Run it only in a trusted repository
and environment.

Risky commands include known mutating or networked tools:

- `rm`
- `pip`
- `npm`
- `python`
- `docker`
- `curl`
- `gh`
- `ssh`
- `scp`
- `uv`
- `wrangler`

Empty commands and unknown commands are risky. This conservative default keeps
new tool names from becoming executable by accident.

## Shell Guard

`src/sac_agent/tools/shell.py` calls the classifier before `subprocess.run()`.
If the command is risky and `allow_risky` is false, the shell tool raises
`ShellCommandBlocked` and does not start a subprocess.

When a command runs, the shell tool returns a structured result with:

- argv
- classification
- return code
- stdout
- stderr

Timeouts and OS errors also become structured failures. Future UI and model
code should display these results instead of treating command failure as an
unhandled crash.

## Approval Gate

`src/sac_agent/runtime/approvals.py` defines:

- `ApprovalKind`
- `ApprovalDecision`
- `ApprovalRequest`
- `ApprovalGate`

The approval gate owns pending requests and recorded decisions. Tool code can
request approval, but it should not decide approval for itself. The TUI or
another human-facing controller should own that decision.

## Patch Workflow

`src/sac_agent/runtime/patches.py` separates patch display from patch
application:

1. A `PatchProposal` carries a summary and unified diff.
2. `changed_files()` parses `diff --git` headers for approval display.
3. The human reviews the diff.
4. After approval, `apply_patch()` sends the diff to `git apply --whitespace=fix`.

The changed-file parser helps the UI show what a patch would touch. It is not
the security boundary for writes. `git apply` remains the authoritative patch
application step.

## Repo Path Guard

`src/sac_agent/tools/repo.py` resolves the repository path and selected file
path before reading a file. `_inside_repo()` rejects paths that escape the repo,
including:

- `../outside.txt`
- absolute paths outside the repo
- symlinks that resolve outside the repo

Future write tools should use the same style of guard before touching paths.

## Teaching Rule

A future model-backed agent can become smarter, but it should not become more
trusted. Keep these boundaries in place:

```text
Read tools are broad.
Write tools are narrow.
Risky shell commands need approval.
Patch application goes through one primitive.
The human owns approval.
```

Chinese note: 模型可以建议操作，不能自己批准危险操作。
