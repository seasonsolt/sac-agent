from pathlib import Path

from sac_agent.runtime.patches import PatchProposal, apply_patch


def test_patch_proposal_summarizes_changed_files():
    patch = PatchProposal(
        summary="Change greeting",
        diff="diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n",
    )

    assert patch.changed_files() == ["app.py"]


def test_apply_patch_changes_file(tmp_path: Path):
    repo = tmp_path
    (repo / "app.py").write_text("print('hello')\n", encoding="utf-8")
    patch = PatchProposal(
        summary="Change greeting",
        diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1 +1 @@\n"
            "-print('hello')\n"
            "+print('hi')\n"
        ),
    )

    result = apply_patch(repo, patch)

    assert result.return_code == 0
    assert (repo / "app.py").read_text(encoding="utf-8") == "print('hi')\n"
