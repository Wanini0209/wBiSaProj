"""LLM task automation base framework.

Provides the abstract base class ``LlmTaskBase``, the ``LlmModel`` enum,
and the editor-driven human-in-the-loop workflow used across all
LLM-assisted automation tasks in ``wsatools``.
"""

import os
import re
import subprocess
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

# ==========================================
# Configuration
# ==========================================
EDITOR = r'"C:\Program Files\Notepad++\notepad++.exe"'
LLM_REQUEST_TMP = "_llm_request.tmp"
LLM_RESPONSE_TMP = "_llm_response.tmp"
UPLOAD_BATCH_MAX_LEN = 240
_HUMAN_ONLY_RE = re.compile(r"(`{3,})human-only[ \t]*\r?\n[\s\S]*?\1(?:\r?\n)?")


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
class LlmTaskBase(ABC):
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
    >>> class MyTask(LlmTaskBase):
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
    # Public methods
    # ------------------------------------------
    def build_prompt(self) -> str:
        """Build the final prompt by substituting template parameters.

        Replaces all ``{{KEY}}`` placeholders in ``PROMPT_TEMPLATE``
        with the corresponding values from ``get_prompt_params()``,
        then strips all ``human-only`` fenced code blocks so that
        human-only content never reaches the LLM.

        Returns
        -------
        str
            The fully assembled and sanitized prompt string.
        """
        prompt = self.PROMPT_TEMPLATE
        for key, value in self.get_prompt_params().items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
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
