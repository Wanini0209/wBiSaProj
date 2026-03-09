"""Tasks for testing.

Methods
-------
cov:
    Check test coverage through `pytest-cov`.
run:
    Run test cases through `pytest`.

"""

from invoke import Context, task

from tasks._common import SOURCE_PACKAGES, USE_PTY, VENV_PREFIX

PYTEST: str = f"{VENV_PREFIX} pytest"


@task(default=True)
def run(ctx: Context, path: str = "") -> None:
    """Run test cases.

    Parameters
    ----------
    ctx : invoke.Context
        The invoke context object.
    path : str, optional
        Specific test path to run. If empty, runs all tests.

    Notes
    -----
    This runs test cases using pytest. When a path is specified,
    only tests in that directory are executed. The USE_PTY flag is
    set based on the platform to ensure proper terminal interaction.

    Examples
    --------
    Run all tests::

        inv test.run

    Run tests for a specific FU::

        inv test.run --path tests/wutils/io/pickle-io/

    """
    cmd = f"{PYTEST} {path}" if path else PYTEST
    ctx.run(cmd, pty=USE_PTY)


@task
def cov(ctx: Context) -> None:
    """Check test coverage.

    Parameters
    ----------
    ctx : invoke.Context
        The invoke context object.

    Notes
    -----
    This runs tests with coverage measurement and generates an HTML
    coverage report. The report will be available in the htmlcov/
    directory and can be opened in a browser for detailed analysis.

    See Also
    --------
    https://pytest-cov.readthedocs.io/
        Documentation for pytest-cov plugin.

    """
    cov_args = " ".join([f"--cov={pkg}" for pkg in SOURCE_PACKAGES])
    ctx.run(f"{PYTEST} {cov_args} --cov-report=html", pty=USE_PTY)
