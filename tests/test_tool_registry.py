from sac_agent.tools.registry import ToolRegistry, default_tool_registry


def test_tool_registry_registers_and_lists_tools():
    registry = ToolRegistry()
    registry.register("example", "Example tool", lambda: "ok")

    assert registry.names() == ["example"]
    assert registry.get("example")() == "ok"


def test_default_registry_contains_repo_tools():
    registry = default_tool_registry()

    assert "git_status" in registry.names()
    assert "list_files" in registry.names()
    assert "read_file" in registry.names()
