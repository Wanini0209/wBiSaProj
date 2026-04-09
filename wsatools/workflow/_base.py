"""Workflow orchestration base framework.

Provides the abstract base class ``Workflow`` for building
multi-step orchestrated workflows that compose LlmTasks,
automation tools, and sub-workflows.

Dependency Direction
--------------------
``workflow`` → ``llm`` (strict one-way dependency).
A workflow may invoke ``LlmTask.run()`` and other workflows,
but ``LlmTask`` must never depend on or invoke workflows.
"""

from abc import ABC, abstractmethod
from typing import Any


class Workflow(ABC):
    """Abstract base class for multi-step orchestrated workflows.

    Subclasses implement ``execute()`` to define the actual
    orchestration logic, composing LlmTasks, automation tools,
    and sub-workflows as needed.

    Examples
    --------
    >>> class MyWorkflow(Workflow):
    ...     def execute(self):
    ...         # Step 1: LLM task
    ...         parsed = SomeLlmTask(model).run()
    ...         # Step 2: automation
    ...         result = some_tool(parsed)
    ...         # Step 3: sub-workflow
    ...         SubWorkflow(result).run()
    ...         return result
    """

    @abstractmethod
    def execute(self) -> Any:
        """Execute the workflow logic.

        Subclasses implement the actual orchestration here,
        composing LlmTasks, automation tools, and sub-workflows.

        Returns
        -------
        Any
            The workflow result.
        """

    def run(self) -> Any:
        """Execute the workflow.

        This method acts as the public entry point using the Template Method
        pattern. Currently, it directly invokes ``execute()``. It is designed
        this way to reserve a stable hook for future cross-cutting concerns
        (e.g., logging, timing, global error handling) without requiring
        modifications to subclasses.

        **Note to developers:** Do NOT override this method. Implement your
        business logic in ``execute()`` instead.

        Returns
        -------
        Any
            The result from ``execute()``.
        """
        return self.execute()
