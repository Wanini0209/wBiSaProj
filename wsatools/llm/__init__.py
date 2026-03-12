"""LLM task automation framework for wsatools.

Provides the base infrastructure for building editor-driven,
human-in-the-loop LLM task workflows.
"""

from wsatools.llm._base import LlmModel, LlmTaskBase

__all__ = ["LlmModel", "LlmTaskBase"]
