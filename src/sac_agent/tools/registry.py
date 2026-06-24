from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sac_agent.tools.repo import git_status, list_files, read_file


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    function: Callable[..., Any]


class ToolRegistry:
    # The registry gives the agent one controlled list of capabilities. New tools
    # become visible through this class, which keeps permission review in one place.
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, name: str, description: str, function: Callable[..., Any]) -> None:
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
    registry = ToolRegistry()
    registry.register("git_status", "Inspect short git status for the repository.", git_status)
    registry.register("list_files", "List repository files as relative paths.", list_files)
    registry.register("read_file", "Read a UTF-8 text file with optional line range.", read_file)
    return registry
