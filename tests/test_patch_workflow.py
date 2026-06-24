from pathlib import Path

from sac_agent.runtime.patches import PatchProposal, apply_patch


def test_patch_proposal_summarizes_changed_files():
    patch = PatchProposal(
        summary="Change greeting",
        diff="diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n",
    )

    assert patch.changed_files() == ["app.py"]


def test_patch_proposal_deduplicates_changed_files_in_order():
    patch = PatchProposal(
        summary="Change files",
        diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "diff --git a/lib.py b/lib.py\n"
            "--- a/lib.py\n"
            "+++ b/lib.py\n"
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
        ),
    )

    assert patch.changed_files() == ["app.py", "lib.py"]


def test_patch_proposal_parses_separator_like_path_text():
    patch = PatchProposal(
        summary="Change tricky path",
        diff=(
            "diff --git a/src/a b/name.py b/src/a b/name.py\n"
            "--- a/src/a b/name.py\n"
            "+++ b/src/a b/name.py\n"
        ),
    )

    assert patch.changed_files() == ["src/a b/name.py"]


def test_patch_proposal_parses_separator_like_renamed_target():
    patch = PatchProposal(summary="Rename", diff="diff --git a/old.py b/src/a b/name.py\n")

    assert patch.changed_files() == ["src/a b/name.py"]


def test_patch_proposal_parses_separator_like_renamed_source():
    patch = PatchProposal(summary="Rename", diff="diff --git a/src/a b/old.py b/new.py\n")

    assert patch.changed_files() == ["new.py"]


def test_patch_proposal_parses_quoted_path_operands():
    patch = PatchProposal(
        summary="Change quoted path",
        diff=(
            'diff --git "a/src/a b/name.py" "b/src/a b/name.py"\n'
            '--- "a/src/a b/name.py"\n'
            '+++ "b/src/a b/name.py"\n'
        ),
    )

    assert patch.changed_files() == ["src/a b/name.py"]


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


def test_apply_patch_returns_nonzero_for_non_applicable_patch(tmp_path: Path):
    repo = tmp_path
    (repo / "app.py").write_text("print('hello')\n", encoding="utf-8")
    patch = PatchProposal(
        summary="Change greeting",
        diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1 +1 @@\n"
            "-print('goodbye')\n"
            "+print('hi')\n"
        ),
    )

    result = apply_patch(repo, patch)

    assert result.return_code != 0
    assert (repo / "app.py").read_text(encoding="utf-8") == "print('hello')\n"


def test_apply_patch_returns_nonzero_for_invalid_repo_path(tmp_path: Path):
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

    result = apply_patch(tmp_path / "missing", patch)

    assert result.return_code != 0
    assert result.stdout == ""
    assert result.stderr
