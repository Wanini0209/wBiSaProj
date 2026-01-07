import time

import pytest

from wutils.wthread import FutureThread


@pytest.mark.unit
class TestFutureThread:
    """Test suite for FutureThread."""

    # === Execution & Result ===

    def test_tc_exec_happy_001_basic_execution(self):
        """TC-EXEC-HAPPY-001: Normal execution and result retrieval.

        Test Objective: Verify the thread executes the Target function and retrieves
        the return value via get_result.
        Expected Result:
        1. get_result() returns the correct value.
        2. done is True.
        3. result attribute is correct, exception attribute is None.
        """

        # Arrange
        def add(a, b):
            return a + b

        t = FutureThread(target=add, args=(1, 2))

        # Act
        t.start()
        res = t.get_result()

        # Assert
        assert res == 3
        assert t.done is True
        assert t.result == 3
        assert t.exception is None

    def test_tc_exec_happy_002_args_passing(self):
        """TC-EXEC-HAPPY-002: Argument passing and standard attributes.

        Test Objective: Verify args, kwargs, name, and daemon parameters are correctly
        passed to the parent class threading.Thread.
        Expected Result: name and daemon attributes are set correctly, and arguments
        are correctly passed to target.
        """

        # Arrange
        def echo(*args, **kwargs):
            return args, kwargs

        # Act
        t = FutureThread(
            target=echo,
            args=(1,),
            kwargs={"k": 2},
            name="MyThread",
            daemon=True,
        )

        # Assert attributes immediately
        assert t.name == "MyThread"
        assert t.daemon is True

        t.start()
        res_args, res_kwargs = t.get_result()

        assert res_args == (1,)
        assert res_kwargs == {"k": 2}

    def test_tc_exec_edge_001_exception_propagation(self):
        """TC-EXEC-EDGE-001: Exception capture and propagation.

        Test Objective: Verify that when the Target raises an exception, get_result
        re-raises that exception, and attribute states are correct.
        Expected Result: get_result raises exception, done is True, exception attribute
        holds that exception.
        """

        # Arrange
        def risky():
            raise ValueError("Boom")

        t = FutureThread(target=risky)

        # Act
        t.start()

        # Assert
        with pytest.raises(ValueError, match="Boom"):
            t.get_result()

        assert t.done is True
        assert t.result is None
        assert isinstance(t.exception, ValueError)

    def test_tc_exec_err_001_timeout(self):
        """TC-EXEC-ERR-001: Wait timeout.

        Test Objective: Verify that TimeoutError is raised when execution time exceeds
        timeout.
        Expected Result: TimeoutError is raised.
        """

        # Arrange
        def slow():
            time.sleep(0.2)

        t = FutureThread(target=slow)
        t.start()

        # Act & Assert
        with pytest.raises(TimeoutError):
            # Timeout is significantly shorter than sleep
            t.get_result(timeout=0.05)

        # Cleanup
        t.join()

    # === State Safety ===

    def test_tc_state_err_001_access_while_running(self):
        """TC-STATE-ERR-001: Attribute access while running (Race Condition Prevention).

        Test Objective: Verify access to result or exception is blocked before the
        thread finishes.
        Expected Result: RuntimeError is raised.
        """

        # Arrange
        def slow():
            time.sleep(0.5)

        t = FutureThread(target=slow)
        t.start()

        # Act & Assert
        assert t.done is False

        with pytest.raises(RuntimeError):
            _ = t.result

        with pytest.raises(RuntimeError):
            _ = t.exception

        # Cleanup
        t.join()

    def test_tc_state_err_002_access_before_start(self):
        """TC-STATE-ERR-002: Attribute access before start.

        Test Objective: Verify access to result is blocked after initialization but
        before calling start().
        Expected Result: RuntimeError is raised.
        """
        # Arrange
        t = FutureThread(target=lambda: None)

        # Act & Assert
        with pytest.raises(RuntimeError):
            _ = t.result
