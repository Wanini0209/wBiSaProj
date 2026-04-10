"""LLM task automation framework for wsatools.

Provides the base infrastructure for building editor-driven,
human-in-the-loop LLM task workflows and quality loops.
"""

from ._base import (
    LlmModel,
    LlmQualityLoop,
    LlmTask,
    QaResult,
    QualityCheckError,
    load_prompt_tags,
)

__all__ = [
    "LlmModel",
    "LlmQualityLoop",
    "LlmTask",
    "QaResult",
    "QualityCheckError",
    "load_prompt_tags",
]
