"""Sample LLM task implementation for developer reference.

This module provides a concrete example of how to subclass
``LlmTask``. It is intended as a reference only and is **not**
exported from the ``wsatools.llm`` package.

See Also
--------
wsatools.llm.LlmTask : The abstract base class.

"""

import json
from typing import Any

from wsatools.llm import LlmModel, LlmTask


class SampleTask(LlmTask):
    """Sample task: analyse code quality of a target file.

    Demonstrates the standard subclass pattern including custom
    ``__init__`` parameters, prompt parameter substitution, file
    uploads, and strict JSON response parsing with validation.

    Parameters
    ----------
    model : LlmModel
        The LLM model to use.
    focus_area : str
        Review focus areas (e.g. "效能與安全性").
    target_file : str
        Absolute path of the file to be reviewed.

    Examples
    --------
    >>> task = SampleTask(
    ...     model=LlmModel.GEMINI_PRO,
    ...     focus_area="效能與安全性",
    ...     target_file="/path/to/script.py",
    ... )
    >>> result = task.run()  # opens editor workflow
    >>> print(result["score"])
    """

    PROMPT_TEMPLATE = """
請幫我進行 Code Review，重點關注以下領域：{{focus_area}}。
請務必以嚴格的 JSON 格式輸出，不要包含任何 Markdown 標記，格式如下：
{
    "score": 85,
    "issues": ["發現的問題 1", "發現的問題 2"],
    "summary": "整體評價"
}
"""

    def __init__(self, model: LlmModel, focus_area: str, target_file: str):
        super().__init__(model)
        self.focus_area = focus_area
        self.target_file = target_file

    def get_prompt_params(self) -> dict[str, str]:
        """Return the focus area for template substitution.

        Returns
        -------
        dict[str, str]
            ``{"focus_area": <self.focus_area>}``.
        """
        return {"focus_area": self.focus_area}

    def get_uploads(self) -> list[str]:
        """Return the target file to upload.

        Returns
        -------
        list[str]
            Single-element list containing ``self.target_file``.
        """
        return [self.target_file]

    def parse(self, response: str) -> dict[str, Any]:
        """Parse and validate the JSON code review response.

        Performs three-stage validation:

        1. Strip Markdown code fences (````json`` / ````)`.
        2. Parse as JSON.
        3. Verify required keys (``score``, ``issues``, ``summary``)
           and value types.

        Parameters
        ----------
        response : str
            Raw LLM response text.

        Returns
        -------
        dict[str, Any]
            Validated review result with keys ``score``, ``issues``,
            and ``summary``.

        Raises
        ------
        json.JSONDecodeError
            If the response is not valid JSON.
        ValueError
            If required keys are missing.
        TypeError
            If ``score`` is not numeric.
        """
        # 1. Strip markdown code block fences
        cleaned = response.replace("```json", "").replace("```", "").strip()

        # 2. Parse JSON
        data = json.loads(cleaned)

        # 3. Business logic validation
        required_keys = {"score", "issues", "summary"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - data.keys()
            raise ValueError(f"JSON 缺少必要的欄位: {missing}")

        if not isinstance(data["score"], (int, float)):
            raise TypeError("欄位 'score' 必須是數字")

        return data
