"""LLM task automation base framework.

Provides the abstract base class ``LlmTask``, the ``LlmModel`` enum,
the ``load_prompt_tags`` helper, the ``LlmQualityLoop`` abstract base
class, and the editor-driven human-in-the-loop workflow used across
all LLM-assisted automation tasks in ``wsatools``.

Public API
----------
LlmTask
    Abstract base class for LLM tasks.
LlmQualityLoop
    Abstract base class for quality loop workflows.
QaResult
    Dataclass for QA task output (passed + report).
QualityCheckError
    Exception raised when max retries are exhausted.
LlmModel
    Enum of available LLM models.
load_prompt_tags
    Load prompt tag files from a directory.
"""

import os
import re
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# ==========================================
# Configuration
# ==========================================
EDITOR = r'"C:\Program Files\Notepad++\notepad++.exe"'
LLM_REQUEST_TMP = "_llm_request.tmp"
LLM_RESPONSE_TMP = "_llm_response.tmp"
UPLOAD_BATCH_MAX_LEN = 240
_HUMAN_ONLY_RE = re.compile(r"(`{3,})human-only[ \t]*\r?\n[\s\S]*?\1(?:\r?\n)?")
_PROMPT_TAG_RE = re.compile(r"(`{3,})prompt-tag:(\S+)[ \t]*\r?\n\1(?:\r?\n)?")


# ==========================================
# Prompt Tag Loader
# ==========================================
def load_prompt_tags(tag_dir: str | Path) -> dict[str, str]:
    """Load prompt tag content from a directory of Markdown files.

    Each ``.md`` file in *tag_dir* becomes a prompt tag: the
    filename (without extension) is the tag ID, and the file
    content is the tag text that replaces the corresponding
    ``prompt-tag`` fenced block in a prompt template.

    Parameters
    ----------
    tag_dir : str | Path
        Directory containing ``.md`` tag files.

    Returns
    -------
    dict[str, str]
        Mapping of tag ID to content.
    """
    tag_dir = Path(tag_dir)
    tags: dict[str, str] = {}
    for path in sorted(tag_dir.glob("*.md")):
        tags[path.stem] = path.read_text(encoding="utf-8")
    return tags


# ==========================================
# LLM Model Enum
# ==========================================
class LlmModel(StrEnum):
    """Available LLM models for task execution.

    Each member's value is the display name shown in the request file,
    guiding the operator to use the correct LLM interface.
    """

    GEMINI_PRO = "Gemini 3 Pro"
    GEMINI_THINK = "Gemini 3 Thinking"
    CLAUDE = "Claude"


# ==========================================
# Abstract Base Class
# ==========================================
class LlmTask(ABC):
    """Abstract base class for all LLM-assisted automation tasks.

    Subclasses define a specific LLM task by providing a prompt template,
    parameter substitution logic, upload file list, and response parser.
    The ``run`` method orchestrates the full human-in-the-loop workflow:
    build prompt → open editor → collect response → parse with retry.

    Parameters
    ----------
    model : LlmModel
        The LLM model to be used for this task.

    Attributes
    ----------
    PROMPT_TEMPLATE : str
        Class-level prompt template containing ``{{KEY}}`` placeholders.
        Subclasses must override this with their own template.

    Examples
    --------
    >>> class MyTask(LlmTask):
    ...     PROMPT_TEMPLATE = "Summarize: {{content}}"
    ...
    ...     def __init__(self, model, content):
    ...         super().__init__(model)
    ...         self.content = content
    ...
    ...     def get_prompt_params(self):
    ...         return {"content": self.content}
    ...
    ...     def get_uploads(self):
    ...         return []
    ...
    ...     def parse(self, response):
    ...         if not response.strip():
    ...             raise ValueError("Empty response")
    ...         return response.strip()
    """

    PROMPT_TEMPLATE: str = ""

    def __init__(self, model: LlmModel):
        self.model = model

    # ------------------------------------------
    # Abstract methods (must be implemented by subclasses)
    # ------------------------------------------
    @abstractmethod
    def get_prompt_params(self) -> dict[str, str]:
        """Return substitution parameters for the prompt template.

        Returns
        -------
        dict[str, str]
            A mapping of ``{{KEY}}`` placeholder names to their
            replacement values. Return an empty dict if the template
            has no placeholders.
        """

    @abstractmethod
    def get_uploads(self) -> list[str]:
        """Return the list of file paths to upload.

        These paths are displayed in the request file to guide the
        operator on which files to upload to the LLM interface.

        Returns
        -------
        list[str]
            Absolute or relative file paths. Return an empty list
            if no files need to be uploaded.
        """

    @abstractmethod
    def parse(self, response: str) -> Any:
        """Parse and validate the raw LLM response.

        This method is called after the operator pastes the LLM output.
        If parsing fails (raises any ``Exception``), the framework
        automatically re-opens the editor for the operator to retry.

        Parameters
        ----------
        response : str
            The raw text content from the LLM response file.

        Returns
        -------
        Any
            The parsed and validated result.

        Raises
        ------
        Exception
            Any exception signals a parse failure, triggering a retry.
        """

    # ------------------------------------------
    # Optional overrides
    # ------------------------------------------
    def get_prompt_tags(self) -> dict[str, str]:
        """Return prompt tag content for template injection.

        Override this method to supply tag content that replaces
        ``prompt-tag`` fenced blocks in the template.  Each key
        corresponds to a ``TAG_ID`` in a block like::

            ```prompt-tag:TAG_ID
            ```

        The entire fenced block is replaced with the value.

        Returns
        -------
        dict[str, str]
            Mapping of tag ID to content.  Empty by default.
        """
        return {}

    # ------------------------------------------
    # Public methods
    # ------------------------------------------
    def build_prompt(self) -> str:
        """Build the final prompt by substituting template parameters.

        Processing order:

        1. Replace ``{{KEY}}`` placeholders with values from
           ``get_prompt_params()``.
        2. Replace ``prompt-tag`` fenced blocks with content from
           ``get_prompt_tags()``.  Unrecognised tag IDs are silently
           removed.
        3. Strip ``human-only`` fenced blocks so that human-only
           content never reaches the LLM.

        Returns
        -------
        str
            The fully assembled and sanitized prompt string.
        """
        prompt = self.PROMPT_TEMPLATE
        for key, value in self.get_prompt_params().items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        tags = self.get_prompt_tags()
        prompt = _PROMPT_TAG_RE.sub(
            lambda m: tags.get(m.group(2), ""),
            prompt,
        )
        prompt = _HUMAN_ONLY_RE.sub("", prompt)
        return prompt

    def run(self) -> Any:
        """Execute the LLM task with retry support.

        Orchestrates the full workflow:

        1. Build prompt and collect upload file list.
        2. Write the request temp file for the operator.
        3. Open editor for the operator to copy prompt to LLM.
        4. Open editor for the operator to paste LLM response.
        5. Parse response; on failure, re-open editor for retry.
        6. Clean up temp files on success.

        Returns
        -------
        Any
            The parsed result from ``parse()``.
        """
        prompt = self.build_prompt()
        uploads = self.get_uploads()

        # Clean up stale temp files
        for tmp in (LLM_REQUEST_TMP, LLM_RESPONSE_TMP):
            if os.path.exists(tmp):
                os.remove(tmp)

        self._prepare_request_file(prompt, uploads)

        is_retry = False
        while True:
            llm_response = self._get_llm_response(is_retry=is_retry)

            if not llm_response.strip():
                print("\n[錯誤] 回應為空，請重新貼上 LLM 回應並存檔。")
                is_retry = True
                continue

            try:
                result = self.parse(llm_response)

                # Parse succeeded; clean up temp files
                os.remove(LLM_REQUEST_TMP)
                os.remove(LLM_RESPONSE_TMP)
                return result

            except Exception as e:
                print(f"\n[解析失敗] 錯誤訊息: {e}")
                print(">> 請在 Notepad++ 中修正 LLM 的回應，" "存檔後關閉以重試...")
                is_retry = True

    # ------------------------------------------
    # Internal methods
    # ------------------------------------------
    def _prepare_request_file(self, prompt: str, uploads: list[str]) -> None:
        """Write the request temp file for operator reference.

        Parameters
        ----------
        prompt : str
            The fully assembled prompt string.
        uploads : list[str]
            File paths to display in the upload section.
        """
        lines = [f"=== LLM Model: {self.model} ===", ""]
        if uploads:
            lines.extend(
                [
                    "--- Upload Files (請依序上傳以下檔案) ---",
                    "(每行為一批，可直接複製整行貼入檔案總管)",
                    "",
                ]
            )
            batch = ""
            for file in uploads:
                fstr = '"' + file.replace("/", "\\") + '"'
                if batch and len(batch) + len(fstr) >= UPLOAD_BATCH_MAX_LEN:
                    lines.append(batch)
                    batch = fstr
                else:
                    batch += fstr
            if batch:
                lines.append(batch)
            lines.append("")

        lines.extend(["--- Prompt (請將以下內容貼入 LLM) ---", "", prompt])

        with open(LLM_REQUEST_TMP, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _get_llm_response(self, is_retry: bool = False) -> str:
        """Open the editor and collect the operator's pasted response.

        Parameters
        ----------
        is_retry : bool, optional
            If ``False`` (first attempt), opens the request file first.
            If ``True`` (retry), skips request and only opens the
            response file. The response file is always cleared before
            opening to prevent stale content from causing loops.
        """
        if not is_retry:
            subprocess.call(
                f"{EDITOR} -multiInst -notabbar -nosession " f"{LLM_REQUEST_TMP}",
                shell=True,
            )

        # Always clear the response file before opening to prevent stale loops
        with open(LLM_RESPONSE_TMP, "w", encoding="utf-8") as f:
            f.write("")

        if is_retry:
            print("\n[系統提示] 已清空舊檔案，" "請重新貼上正確的回應，存檔後關閉。")
        else:
            print("\n等待 LLM 回應中... " "(請在 Notepad++ 貼上結果，存檔後關閉)")

        subprocess.call(
            f"{EDITOR} -multiInst -notabbar -nosession " f"{LLM_RESPONSE_TMP}",
            shell=True,
        )

        with open(LLM_RESPONSE_TMP, encoding="utf-8") as f:
            return f.read()


# ==========================================
# QA Result
# ==========================================
@dataclass
class QaResult:
    """Quality review result.

    Attributes
    ----------
    passed : bool
        True if all checks passed, False if issues were found.
    report : str
        Full QA output text.  A brief confirmation when passed,
        or an issue list with fix directions when failed.
    """

    passed: bool
    report: str


# ==========================================
# Quality Check Error
# ==========================================
class QualityCheckError(Exception):
    """Raised when the quality loop exhausts all retries.

    Attributes
    ----------
    report : str
        The last QA report describing unresolved issues.
    """

    def __init__(self, report: str):
        self.report = report
        super().__init__(
            f"Quality check failed after max retries. " f"Last report:\n{report}"
        )


# ==========================================
# Quality Loop Base Class
# ==========================================
class LlmQualityLoop(ABC):
    """Abstract base class for LLM quality loops.

    Subclasses override factory methods to provide the three
    concrete ``LlmTask`` instances (Generate, QA, Fix).
    ``run()`` implements the Template Method pattern to control
    the iteration cycle.

    Parameters
    ----------
    draft_path : str
        Path for the draft file.  The framework writes
        Generate/Fix output here for QA/Fix tasks to upload.
    max_retries : int, optional
        Maximum number of Fix attempts after QA failure,
        by default 2.  The loop executes at most 1 Generate
        + (max_retries + 1) QA + max_retries Fix calls.
    """

    def __init__(self, draft_path: str, max_retries: int = 2):
        self.draft_path = draft_path
        self.max_retries = max_retries

    # ------------------------------------------
    # Factory methods (subclasses MUST override)
    # ------------------------------------------

    @abstractmethod
    def create_generate_task(self) -> LlmTask:
        """Create the Generate task.

        Returns
        -------
        LlmTask
            A task whose ``run()`` returns ``str``.
        """

    @abstractmethod
    def create_qa_task(self) -> LlmTask:
        """Create the QA task.

        Called after ``draft_path`` has been written with content
        to review.

        Returns
        -------
        LlmTask
            A task whose ``run()`` returns ``QaResult``.
        """

    @abstractmethod
    def create_fix_task(self, qa_report: str) -> LlmTask:
        """Create the Fix task.

        Called when QA has failed.  ``draft_path`` contains the
        content to fix, and ``qa_report`` describes the issues.

        Parameters
        ----------
        qa_report : str
            The QA report describing what needs to be fixed.

        Returns
        -------
        LlmTask
            A task whose ``run()`` returns ``str``.
        """

    # ------------------------------------------
    # Hook methods (subclasses MAY override)
    # ------------------------------------------

    def on_generate_complete(self, content: str) -> None:  # noqa: B027
        """Hook called after Generate task completes.

        Parameters
        ----------
        content : str
            The generated content.
        """

    def on_qa_complete(self, qa_result: QaResult, attempt: int) -> None:  # noqa: B027
        """Hook called after each QA task completes.

        Parameters
        ----------
        qa_result : QaResult
            The QA result.
        attempt : int
            Zero-based attempt index (0 = first QA after Generate).
        """

    def on_fix_complete(self, content: str, attempt: int) -> None:  # noqa: B027
        """Hook called after each Fix task completes.

        Parameters
        ----------
        content : str
            The fixed content.
        attempt : int
            Zero-based attempt index (0 = first Fix).
        """

    # ------------------------------------------
    # Template method
    # ------------------------------------------

    def run(self) -> str:
        """Execute the quality loop.

        Flow:

        1. Call Generate Task to produce initial content.
        2. Write content to ``draft_path``.
        3. Call QA Task to review.
        4. If PASS → return content.
        5. If FAIL → Call Fix Task → write to ``draft_path`` → go to 3.
        6. If max retries exceeded → raise ``QualityCheckError``.

        Returns
        -------
        str
            The content that passed QA.

        Raises
        ------
        QualityCheckError
            When QA fails after exhausting all retries.
        """
        content = self.create_generate_task().run()
        self._write_draft(content)
        self.on_generate_complete(content)

        for attempt in range(self.max_retries + 1):
            qa_result = self.create_qa_task().run()
            self.on_qa_complete(qa_result, attempt)

            if qa_result.passed:
                return content

            if attempt < self.max_retries:
                content = self.create_fix_task(qa_result.report).run()
                self._write_draft(content)
                self.on_fix_complete(content, attempt)

        raise QualityCheckError(qa_result.report)

    # ------------------------------------------
    # Internal helpers
    # ------------------------------------------

    def _write_draft(self, content: str) -> None:
        """Write content to the draft file.

        Creates parent directories if they do not exist.

        Parameters
        ----------
        content : str
            The content to write.
        """
        path = Path(self.draft_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
