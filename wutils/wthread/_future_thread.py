"""Implementation module for _future_thread.py."""

import sys
import threading
from collections.abc import Callable
from typing import Any


class FutureThread[T](threading.Thread):
    """
    A thread subclass that captures the return value or exception of a target function.

    This class mimics the behavior of a Future, allowing the caller to wait for
    the result or check the status of the thread execution.
    """

    def __init__(  # noqa: PLR0913
        self,
        group: None = None,
        target: Callable[..., T] | None = None,
        name: str | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        *,
        daemon: bool | None = None,
    ) -> None:
        """
        Initialize the FutureThread instance.

        Parameters
        ----------
        group : None
            Reserved parameter, must be None (for compatibility with threading.Thread).
        target : Optional[Callable[..., T]]
            The callable object to be invoked by the run() method.
        name : Optional[str]
            The thread name.
        args : tuple
            The argument tuple for the target invocation.
        kwargs : Optional[dict]
            The dictionary of keyword arguments for the target invocation.
        daemon : Optional[bool]
            If True, the thread is a daemon thread.

        Returns
        -------
        None
        """
        # Implements Rule-01: Standard Thread compatibility and initialization
        super().__init__(
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )
        self._return_value: T | None = None
        self._exception: BaseException | None = None
        self._completion_event = threading.Event()

    def run(self) -> None:
        """
        Execute the thread's activity.

        This method overrides threading.Thread.run() to capture the return value
        or exception.

        Returns
        -------
        None
        """
        # Implements Rule-08: Execution encapsulation and capture
        try:
            if self._target:
                self._return_value = self._target(*self._args, **self._kwargs)
        except BaseException:
            # Implements Rule-08: Failure handling using sys.exc_info()
            # Implements Rule-09: Avoid circular reference by only storing the value,
            # ensuring compliance with NFR-01 (Resource Management).
            self._exception = sys.exc_info()[1]
        finally:
            # Implements Rule-08: Always set completion signal
            self._completion_event.set()

    def get_result(self, timeout: float | None = None) -> T:
        """
        Wait for the thread to complete and return the result.

        If the thread raised an exception, it is re-raised here.

        Parameters
        ----------
        timeout : Optional[float]
            The maximum number of seconds to wait. If None, wait indefinitely.

        Returns
        -------
        T
            The return value of the target function.

        Raises
        ------
        TimeoutError
            If the thread does not complete within the timeout period.
        BaseException
            If the target function raised an exception during execution.
        """
        # Implements Rule-02: Synchronous wait
        if not self._completion_event.wait(timeout):
            # Implements Rule-04: Timeout handling
            raise TimeoutError("The thread execution timed out.")

        # Implements Rule-03: Exception re-raise
        if self._exception:
            raise self._exception

        # Implements Rule-02: Return result
        # We rely on the guarantee that if no exception occurred, execution succeeded
        return self._return_value  # type: ignore

    @property
    def done(self) -> bool:
        """
        Check if the thread has finished execution (successfully or with an error).

        Returns
        -------
        bool
            True if the thread has finished, False otherwise.
        """
        # Implements Rule-05: Execution state query
        return self._completion_event.is_set()

    @property
    def result(self) -> T | None:
        """
        Get the execution result without waiting.

        Returns
        -------
        Optional[T]
            The return value if successful, or None if failed or not applicable.

        Raises
        ------
        RuntimeError
            If the thread has not finished execution yet.
        """
        # Implements Rule-06: Safe property access check
        if not self.done:
            raise RuntimeError("Thread has not finished execution.")

        # Implements Rule-07: Silent result access (None on failure)
        if self._exception:
            return None
        return self._return_value

    @property
    def exception(self) -> BaseException | None:
        """
        Get the captured exception object.

        Returns
        -------
        Optional[BaseException]
            The exception object if execution failed, or None if successful.

        Raises
        ------
        RuntimeError
            If the thread has not finished execution yet.
        """
        # Implements Rule-06: Safe property access check
        if not self.done:
            raise RuntimeError("Thread has not finished execution.")

        # Implements Rule-07: Silent exception access (None on success)
        return self._exception
