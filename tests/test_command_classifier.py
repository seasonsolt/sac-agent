from sac_agent.runtime.commands import CommandRisk, classify_command


def test_classifies_read_only_commands_as_safe():
    assert classify_command(["git", "status"]).risk == CommandRisk.SAFE
    assert classify_command(["rg", "AgentSession"]).risk == CommandRisk.SAFE
    assert classify_command(["pytest", "-q"]).risk == CommandRisk.SAFE


def test_classifies_mutating_or_network_commands_as_risky():
    assert classify_command(["rm", "-rf", "src"]).risk == CommandRisk.RISKY
    assert classify_command(["pip", "install", "requests"]).risk == CommandRisk.RISKY
    assert classify_command(["gh", "repo", "create"]).risk == CommandRisk.RISKY
