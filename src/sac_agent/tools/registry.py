from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sac_agent.tools.repo import git_status, list_files, read_file
from sac_agent.tools.shell import run_shell_command


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    function: Callable[..., Any]


class ToolRegistry:
    # The registry gives the agent one controlled list of capabilities. Future
    # DeepAgent adapters should expose tools from here instead of importing helper
    # functions directly, which keeps permission review in one place.
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, name: str, description: str, function: Callable[..., Any]) -> None:
        # Descriptions matter because model-backed runners will use them to decide
        # when a tool is appropriate. Keep them factual and permission-aware.
        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            function=function,
        )

    def get(self, name: str) -> Callable[..., Any]:
        return self._tools[name].function

    def names(self) -> list[str]:
        return sorted(self._tools)

    def all(self) -> list[RegisteredTool]:
        return [self._tools[name] for name in self.names()]


def default_tool_registry() -> ToolRegistry:
    # The default set is small on purpose: broad read tools, plus a shell tool that
    # performs its own risk check. Add write tools only with approval coverage.
    registry = ToolRegistry()
    registry.register("git_status", "Inspect short git status for the repository.", git_status)
    registry.register("list_files", "List repository files as relative paths.", list_files)
    registry.register("read_file", "Read a UTF-8 text file with optional line range.", read_file)
    registry.register("run_shell_command", "Run a classified shell command in the repository.", run_shell_command)
    return registry
