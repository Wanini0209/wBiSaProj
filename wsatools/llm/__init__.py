"""LLM task automation framework for wsatools.

Provides the base infrastructure for building editor-driven,
human-in-the-loop LLM task workflows.
"""

from wsatools.llm._base import LlmModel, LlmTask, load_prompt_tags

__all__ = ["LlmModel", "LlmTask", "load_prompt_tags"]
