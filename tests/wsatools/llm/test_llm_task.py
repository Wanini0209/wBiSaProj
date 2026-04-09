"""Framework-level unit tests for LlmTask and load_prompt_tags.

Tests the three build_prompt processing stages (placeholder
substitution, prompt-tag insertion, human-only stripping) and
the load_prompt_tags directory loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from wsatools.llm import LlmModel, LlmTask, load_prompt_tags


# ==========================================
# Mock infrastructure
# ==========================================
class _MockTask(LlmTask):
    """Minimal concrete subclass for testing build_prompt."""

    PROMPT_TEMPLATE = ""

    def __init__(
        self,
        template: str,
        params: dict[str, str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        super().__init__(LlmModel.CLAUDE)
        self.PROMPT_TEMPLATE = template
        self._params = params or {}
        self._tags = tags or {}

    def get_prompt_params(self) -> dict[str, str]:
        return self._params

    def get_prompt_tags(self) -> dict[str, str]:
        return self._tags

    def get_uploads(self) -> list[str]:
        return []

    def parse(self, response: str) -> Any:
        return response


# ==========================================
# A. Placeholder substitution
# ==========================================
@pytest.mark.unit
class TestPlaceholderSubstitution:
    """build_prompt replaces {{KEY}} placeholders."""

    def test_single_placeholder(self) -> None:
        """A single placeholder is replaced with its value."""
        task = _MockTask(
            template="Hello, {{NAME}}!",
            params={"NAME": "World"},
        )

        result = task.build_prompt()

        assert result == "Hello, World!"

    def test_multiple_placeholders(self) -> None:
        """Multiple different placeholders are all replaced."""
        task = _MockTask(
            template="{{LIBRARY}}/{{TOOLKIT}} overview",
            params={"LIBRARY": "wutils", "TOOLKIT": "io"},
        )

        result = task.build_prompt()

        assert result == "wutils/io overview"

    def test_repeated_placeholder(self) -> None:
        """The same placeholder appearing multiple times is replaced everywhere."""
        task = _MockTask(
            template="{{X}} and {{X}} again",
            params={"X": "value"},
        )

        result = task.build_prompt()

        assert result == "value and value again"

    def test_no_placeholders(self) -> None:
        """Template without placeholders is returned unchanged."""
        task = _MockTask(template="No placeholders here.")

        result = task.build_prompt()

        assert result == "No placeholders here."

    def test_empty_params(self) -> None:
        """Empty params dict leaves unmatched placeholders intact."""
        task = _MockTask(template="Keep {{THIS}}", params={})

        result = task.build_prompt()

        assert result == "Keep {{THIS}}"


# ==========================================
# B. Human-only stripping
# ==========================================
@pytest.mark.unit
class TestHumanOnlyStripping:
    """build_prompt removes human-only fenced code blocks."""

    def test_strips_human_only_block(self) -> None:
        """A human-only block is completely removed."""
        task = _MockTask(
            template=(
                "Before\n"
                "```human-only\n"
                "This is for humans only.\n"
                "```\n"
                "After"
            ),
        )

        result = task.build_prompt()

        assert "humans only" not in result
        assert "human-only" not in result
        assert "Before" in result
        assert "After" in result

    def test_strips_multiline_human_only(self) -> None:
        """Multi-line human-only block is fully removed."""
        task = _MockTask(
            template=(
                "# Section\n"
                "```human-only\n"
                "Ref: DESIGN.md §1\n"
                "Ref: DESIGN.md §2\n"
                "```\n"
                "Content here."
            ),
        )

        result = task.build_prompt()

        assert "Ref:" not in result
        assert "Content here." in result

    def test_strips_with_four_backticks(self) -> None:
        """Human-only block using four backticks is also stripped."""
        task = _MockTask(
            template=("Start\n" "````human-only\n" "Hidden content.\n" "````\n" "End"),
        )

        result = task.build_prompt()

        assert "Hidden content" not in result
        assert "Start" in result
        assert "End" in result

    def test_preserves_non_human_only_blocks(self) -> None:
        """Regular fenced code blocks are not stripped."""
        task = _MockTask(
            template=("```python\n" "print('hello')\n" "```"),
        )

        result = task.build_prompt()

        assert "print('hello')" in result

    def test_multiple_human_only_blocks(self) -> None:
        """Multiple human-only blocks are all removed."""
        task = _MockTask(
            template=(
                "A\n"
                "```human-only\n"
                "Block 1\n"
                "```\n"
                "B\n"
                "```human-only\n"
                "Block 2\n"
                "```\n"
                "C"
            ),
        )

        result = task.build_prompt()

        assert "Block 1" not in result
        assert "Block 2" not in result
        assert "A" in result
        assert "B" in result
        assert "C" in result


# ==========================================
# C. Prompt-tag insertion
# ==========================================
@pytest.mark.unit
class TestPromptTagInsertion:
    """build_prompt replaces prompt-tag blocks with tag content."""

    def test_replaces_prompt_tag(self) -> None:
        """A prompt-tag block is replaced with the corresponding tag content."""
        task = _MockTask(
            template=(
                "# Context\n"
                "\n"
                "```prompt-tag:MY_TAG\n"
                "```\n"
                "\n"
                "# Next Section"
            ),
            tags={"MY_TAG": "Injected tag content.\n"},
        )

        result = task.build_prompt()

        assert "Injected tag content." in result
        assert "prompt-tag" not in result
        assert "# Context" in result
        assert "# Next Section" in result

    def test_unknown_tag_removed_silently(self) -> None:
        """A prompt-tag with an unrecognised ID is silently removed."""
        task = _MockTask(
            template=("Before\n" "```prompt-tag:UNKNOWN\n" "```\n" "After"),
            tags={},
        )

        result = task.build_prompt()

        assert "prompt-tag" not in result
        assert "UNKNOWN" not in result
        assert "Before" in result
        assert "After" in result

    def test_multiple_tags(self) -> None:
        """Multiple prompt-tag blocks are each replaced independently."""
        task = _MockTask(
            template=(
                "```prompt-tag:TAG_A\n" "```\n" "---\n" "```prompt-tag:TAG_B\n" "```"
            ),
            tags={"TAG_A": "Content A\n", "TAG_B": "Content B\n"},
        )

        result = task.build_prompt()

        assert "Content A" in result
        assert "Content B" in result
        assert "prompt-tag" not in result

    def test_four_backtick_tag(self) -> None:
        """Prompt-tag with four backticks is matched correctly."""
        task = _MockTask(
            template=("````prompt-tag:QUAD\n" "````\n" "Done"),
            tags={"QUAD": "Four-tick content.\n"},
        )

        result = task.build_prompt()

        assert "Four-tick content." in result
        assert "Done" in result

    def test_default_get_prompt_tags_returns_empty(self) -> None:
        """Default get_prompt_tags returns empty dict (tag blocks removed)."""

        class _NoTagTask(_MockTask):
            def get_prompt_tags(self) -> dict[str, str]:
                return super(_MockTask, self).get_prompt_tags()

        task = _NoTagTask(
            template=("Before\n" "```prompt-tag:ANY\n" "```\n" "After"),
        )

        result = task.build_prompt()

        assert "prompt-tag" not in result
        assert "Before" in result
        assert "After" in result


# ==========================================
# D. Combined processing
# ==========================================
@pytest.mark.unit
class TestCombinedProcessing:
    """All three mechanisms work together in correct order."""

    def test_placeholder_then_tag_then_human_only(self) -> None:
        """Placeholders, prompt-tags, and human-only blocks are all processed."""
        task = _MockTask(
            template=(
                "# Overview: {{LIBRARY}}\n"
                "\n"
                "```human-only\n"
                "Ref: SOURCE.md §1\n"
                "```\n"
                "\n"
                "```prompt-tag:CONTEXT\n"
                "```\n"
                "\n"
                "Target: {{TOOLKIT}}"
            ),
            params={"LIBRARY": "wutils", "TOOLKIT": "io"},
            tags={"CONTEXT": "Shared project context.\n"},
        )

        result = task.build_prompt()

        assert "wutils" in result
        assert "io" in result
        assert "Shared project context." in result
        assert "human-only" not in result
        assert "Ref: SOURCE.md" not in result
        assert "prompt-tag" not in result
        assert "{{" not in result


# ==========================================
# E. load_prompt_tags
# ==========================================
@pytest.mark.unit
class TestLoadPromptTags:
    """load_prompt_tags reads .md files from a directory."""

    def test_loads_single_file(self, tmp_path: Path) -> None:
        """A single .md file becomes a tag entry."""
        (tmp_path / "MY_TAG.md").write_text(
            "Tag content here.\n",
            encoding="utf-8",
        )

        tags = load_prompt_tags(tmp_path)

        assert tags == {"MY_TAG": "Tag content here.\n"}

    def test_loads_multiple_files(self, tmp_path: Path) -> None:
        """Multiple .md files are all loaded."""
        (tmp_path / "TAG_A.md").write_text("A\n", encoding="utf-8")
        (tmp_path / "TAG_B.md").write_text("B\n", encoding="utf-8")

        tags = load_prompt_tags(tmp_path)

        assert len(tags) == 2
        assert tags["TAG_A"] == "A\n"
        assert tags["TAG_B"] == "B\n"

    def test_ignores_non_md_files(self, tmp_path: Path) -> None:
        """Non-.md files are ignored."""
        (tmp_path / "TAG.md").write_text("Yes\n", encoding="utf-8")
        (tmp_path / "README.txt").write_text("No\n", encoding="utf-8")

        tags = load_prompt_tags(tmp_path)

        assert list(tags.keys()) == ["TAG"]

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Empty directory returns empty dict."""
        tags = load_prompt_tags(tmp_path)

        assert tags == {}

    def test_filename_becomes_tag_id(self, tmp_path: Path) -> None:
        """Tag ID is the filename stem (without .md extension)."""
        (tmp_path / "INIT_TOOLKIT_CONTEXT_L2.md").write_text(
            "context\n",
            encoding="utf-8",
        )

        tags = load_prompt_tags(tmp_path)

        assert "INIT_TOOLKIT_CONTEXT_L2" in tags

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        """String paths are accepted (not just Path objects)."""
        (tmp_path / "TAG.md").write_text("ok\n", encoding="utf-8")

        tags = load_prompt_tags(str(tmp_path))

        assert tags == {"TAG": "ok\n"}
