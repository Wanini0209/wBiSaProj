"""Framework-level unit tests for LlmQualityLoop.

Uses mock Task subclasses to test the quality loop framework
without real LLM interaction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from wsatools.llm import (
    LlmModel,
    LlmQualityLoop,
    LlmTask,
    QaResult,
    QualityCheckError,
)


# ==========================================
# Mock infrastructure
# ==========================================
class _MockTask(LlmTask):
    """A mock LlmTask that returns a pre-configured output."""

    PROMPT_TEMPLATE = "mock"

    def __init__(self, output: Any) -> None:
        super().__init__(LlmModel.CLAUDE)
        self._output = output

    def get_prompt_params(self) -> dict[str, str]:
        return {}

    def get_uploads(self) -> list[str]:
        return []

    def parse(self, response: str) -> Any:
        return response

    def run(self) -> Any:
        """Skip the editor workflow, directly return the output."""
        return self._output


class _MockQualityLoop(LlmQualityLoop):
    """A concrete QualityLoop subclass for testing.

    Parameters
    ----------
    draft_path : str
        Path for draft file.
    gen_output : str
        Output from the generate task.
    qa_results : list[QaResult]
        Sequence of QA results to return on each call.
    fix_outputs : list[str]
        Sequence of fix outputs to return on each call.
    max_retries : int
        Maximum retries.
    """

    def __init__(
        self,
        draft_path: str,
        gen_output: str,
        qa_results: list[QaResult],
        fix_outputs: list[str] | None = None,
        max_retries: int = 2,
    ) -> None:
        super().__init__(draft_path=draft_path, max_retries=max_retries)
        self._gen_output = gen_output
        self._qa_iter = iter(qa_results)
        self._fix_iter = iter(fix_outputs or [])

        # Tracking for assertions
        self.generate_calls: list[str] = []
        self.qa_calls: list[QaResult] = []
        self.fix_calls: list[tuple[str, str]] = []
        self.hook_generate: list[str] = []
        self.hook_qa: list[tuple[QaResult, int]] = []
        self.hook_fix: list[tuple[str, int]] = []

    def create_generate_task(self) -> LlmTask:
        self.generate_calls.append(self._gen_output)
        return _MockTask(self._gen_output)

    def create_qa_task(self) -> LlmTask:
        result = next(self._qa_iter)
        self.qa_calls.append(result)
        return _MockTask(result)

    def create_fix_task(self, qa_report: str) -> LlmTask:
        output = next(self._fix_iter)
        self.fix_calls.append((qa_report, output))
        return _MockTask(output)

    def on_generate_complete(self, content: str) -> None:
        self.hook_generate.append(content)

    def on_qa_complete(self, qa_result: QaResult, attempt: int) -> None:
        self.hook_qa.append((qa_result, attempt))

    def on_fix_complete(self, content: str, attempt: int) -> None:
        self.hook_fix.append((content, attempt))


# ==========================================
# A. QaResult
# ==========================================
@pytest.mark.unit
class TestQaResult:
    """QaResult dataclass field access."""

    def test_pass_result(self) -> None:
        """PASS result stores fields correctly."""
        result = QaResult(passed=True, report="All checks passed.")

        assert result.passed is True
        assert result.report == "All checks passed."

    def test_fail_result(self) -> None:
        """FAIL result stores fields correctly."""
        result = QaResult(passed=False, report="Issue: wrong description.")

        assert result.passed is False
        assert result.report == "Issue: wrong description."


# ==========================================
# B. QualityCheckError
# ==========================================
@pytest.mark.unit
class TestQualityCheckError:
    """QualityCheckError exception behavior."""

    def test_stores_report(self) -> None:
        """Exception stores the report attribute."""
        error = QualityCheckError("Some failures found.")

        assert error.report == "Some failures found."

    def test_str_contains_report(self) -> None:
        """String representation includes the report."""
        error = QualityCheckError("Detail: missing section.")

        assert "Detail: missing section." in str(error)

    def test_is_exception(self) -> None:
        """QualityCheckError is an Exception subclass."""
        assert issubclass(QualityCheckError, Exception)


# ==========================================
# C. run() — Generate → QA PASS
# ==========================================
@pytest.mark.unit
class TestRunPassOnFirstQa:
    """QA passes on the first attempt after Generate."""

    def test_returns_generated_content(self, tmp_path: Path) -> None:
        """run() returns the Generate output when QA passes."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="generated content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        result = loop.run()

        assert result == "generated content"

    def test_draft_file_written(self, tmp_path: Path) -> None:
        """Draft file contains the generated content."""
        draft = tmp_path / "draft.md"
        loop = _MockQualityLoop(
            draft_path=str(draft),
            gen_output="generated content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert draft.read_text(encoding="utf-8") == "generated content"

    def test_fix_not_called(self, tmp_path: Path) -> None:
        """Fix task is never created when QA passes immediately."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="generated content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert loop.fix_calls == []

    def test_generate_called_once(self, tmp_path: Path) -> None:
        """Generate task is created exactly once."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert len(loop.generate_calls) == 1


# ==========================================
# D. run() — Generate → QA FAIL → Fix → QA PASS
# ==========================================
@pytest.mark.unit
class TestRunPassAfterFix:
    """QA fails first, then passes after one Fix."""

    def test_returns_fixed_content(self, tmp_path: Path) -> None:
        """run() returns the Fix output, not the original Generate output."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="Issue: X"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fixed"],
        )

        result = loop.run()

        assert result == "fixed"

    def test_fix_receives_qa_report(self, tmp_path: Path) -> None:
        """Fix task receives the QA report as input."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="Issue: wrong desc"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fixed"],
        )

        loop.run()

        assert len(loop.fix_calls) == 1
        assert loop.fix_calls[0][0] == "Issue: wrong desc"

    def test_draft_file_updated_after_fix(self, tmp_path: Path) -> None:
        """Draft file is overwritten with the fixed content."""
        draft = tmp_path / "draft.md"
        loop = _MockQualityLoop(
            draft_path=str(draft),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="Issue"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fixed"],
        )

        loop.run()

        assert draft.read_text(encoding="utf-8") == "fixed"


# ==========================================
# E. run() — Exceeds max retries
# ==========================================
@pytest.mark.unit
class TestRunExceedsRetries:
    """QA never passes, max retries exhausted."""

    def test_raises_quality_check_error(self, tmp_path: Path) -> None:
        """run() raises QualityCheckError when retries exhausted."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="Issue 1"),
                QaResult(passed=False, report="Issue 2"),
                QaResult(passed=False, report="Issue 3"),
            ],
            fix_outputs=["fix-1", "fix-2"],
            max_retries=2,
        )

        with pytest.raises(QualityCheckError) as exc_info:
            loop.run()

        assert exc_info.value.report == "Issue 3"

    def test_fix_called_max_retries_times(self, tmp_path: Path) -> None:
        """Fix is called exactly max_retries times."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="A"),
                QaResult(passed=False, report="B"),
                QaResult(passed=False, report="C"),
            ],
            fix_outputs=["fix-1", "fix-2"],
            max_retries=2,
        )

        with pytest.raises(QualityCheckError):
            loop.run()

        assert len(loop.fix_calls) == 2

    def test_qa_called_max_retries_plus_one_times(
        self,
        tmp_path: Path,
    ) -> None:
        """QA is called max_retries + 1 times (initial + after each fix)."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="A"),
                QaResult(passed=False, report="B"),
                QaResult(passed=False, report="C"),
            ],
            fix_outputs=["fix-1", "fix-2"],
            max_retries=2,
        )

        with pytest.raises(QualityCheckError):
            loop.run()

        assert len(loop.qa_calls) == 3

    def test_max_retries_zero(self, tmp_path: Path) -> None:
        """With max_retries=0, no Fix is attempted."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[QaResult(passed=False, report="Fail")],
            max_retries=0,
        )

        with pytest.raises(QualityCheckError) as exc_info:
            loop.run()

        assert exc_info.value.report == "Fail"
        assert loop.fix_calls == []


# ==========================================
# F. Hook methods
# ==========================================
@pytest.mark.unit
class TestHookMethods:
    """Hook methods are called at the correct points."""

    def test_on_generate_complete_called(self, tmp_path: Path) -> None:
        """on_generate_complete is called after Generate."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert loop.hook_generate == ["content"]

    def test_on_qa_complete_called_with_attempt(
        self,
        tmp_path: Path,
    ) -> None:
        """on_qa_complete is called after each QA with incrementing attempt."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="A"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fixed"],
        )

        loop.run()

        assert len(loop.hook_qa) == 2
        assert loop.hook_qa[0] == (QaResult(passed=False, report="A"), 0)
        assert loop.hook_qa[1] == (QaResult(passed=True, report="OK"), 1)

    def test_on_fix_complete_called_with_attempt(
        self,
        tmp_path: Path,
    ) -> None:
        """on_fix_complete is called after each Fix with incrementing attempt."""
        loop = _MockQualityLoop(
            draft_path=str(tmp_path / "draft.md"),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="A"),
                QaResult(passed=False, report="B"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fix-1", "fix-2"],
        )

        loop.run()

        assert len(loop.hook_fix) == 2
        assert loop.hook_fix[0] == ("fix-1", 0)
        assert loop.hook_fix[1] == ("fix-2", 1)


# ==========================================
# G. Draft file management
# ==========================================
@pytest.mark.unit
class TestDraftFileManagement:
    """Draft file is correctly managed by the framework."""

    def test_draft_contains_generated_content(
        self,
        tmp_path: Path,
    ) -> None:
        """After Generate, draft file has the generated content."""
        draft = tmp_path / "draft.md"
        loop = _MockQualityLoop(
            draft_path=str(draft),
            gen_output="initial content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert draft.read_text(encoding="utf-8") == "initial content"

    def test_draft_updated_after_fix(self, tmp_path: Path) -> None:
        """After Fix, draft file is overwritten with fixed content."""
        draft = tmp_path / "draft.md"
        loop = _MockQualityLoop(
            draft_path=str(draft),
            gen_output="original",
            qa_results=[
                QaResult(passed=False, report="Issue"),
                QaResult(passed=True, report="OK"),
            ],
            fix_outputs=["fixed version"],
        )

        loop.run()

        assert draft.read_text(encoding="utf-8") == "fixed version"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Parent directories are created if they don't exist."""
        draft = tmp_path / "deep" / "nested" / "draft.md"
        loop = _MockQualityLoop(
            draft_path=str(draft),
            gen_output="content",
            qa_results=[QaResult(passed=True, report="OK")],
        )

        loop.run()

        assert draft.exists()
        assert draft.read_text(encoding="utf-8") == "content"
