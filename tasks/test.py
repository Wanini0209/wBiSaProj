"""Tasks for testing.

Methods
-------
cov:
    Check test coverage through `pytest-cov`.
llm:
    Run LLM-marked test cases through `pytest`.
run:
    Run test cases through `pytest` (excludes LLM tests).

"""

from invoke import Context, task

from tasks._common import SOURCE_PACKAGES, USE_PTY, VENV_PREFIX

PYTEST: str = f"{VENV_PREFIX} pytest"


@task(default=True)
def run(ctx: Context, path: str = "", k: str = "") -> None:
    """Run test cases (excluding LLM tests).

    Parameters
    ----------
    ctx : invoke.Context
        The invoke context object.
    path : str, optional
        Specific test path to run. If empty, runs all tests.
    k : str, optional
        Pytest ``-k`` expression for filtering test names.

    Notes
    -----
    This runs **general** test cases using pytest, automatically
    excluding tests marked with ``@pytest.mark.llm``.  Use
    ``inv test.llm`` to run LLM-specific tests instead.

    Examples
    --------
    Run all general tests::

        inv test

    Run tests for a specific path::

        inv test --path tests/wutils/io/pickle-io/

    Run tests matching a keyword expression::

        inv test --k test_workflow

    Combine path and keyword filtering::

        inv test --path tests/wsatools/llm/library/l3_entry/ --k test_add_qa

    """
    parts = [PYTEST, '-m "not llm"']
    if path:
        parts.append(path)
    if k:
        parts.append(f'-k "{k}"')
    ctx.run(" ".join(parts), pty=USE_PTY)


@task
def llm(ctx: Context, path: str = "", k: str = "") -> None:
    """Run LLM-marked test cases.

    Parameters
    ----------
    ctx : invoke.Context
        The invoke context object.
    path : str, optional
        Specific test path to run. If empty, runs all LLM tests.
    k : str, optional
        Pytest ``-k`` expression for filtering test names.

    Notes
    -----
    This runs **only** tests marked with ``@pytest.mark.llm``.
    LLM tests typically require human-in-the-loop operation or
    access to LLM services, and are therefore excluded from
    ``inv test`` and ``inv test.cov`` by default.

    Run manually::

        inv test.llm

    Examples
    --------
    Run all LLM tests::

        inv test.llm

    Run LLM tests matching a keyword::

        inv test.llm --k test_add_qa_llm

    Run LLM tests under a specific path::

        inv test.llm --path tests/wsatools/llm/library/l3_entry/

    Combine path and keyword::

        inv test.llm --path tests/wsatools/llm/library/l3_entry/ --k test_add_qa_llm

    """
    parts = [PYTEST, '-m "llm"']
    if path:
        parts.append(path)
    if k:
        parts.append(f'-k "{k}"')
    ctx.run(" ".join(parts), pty=USE_PTY)


@task
def cov(ctx: Context) -> None:
    """Check test coverage (excluding LLM tests).

    Parameters
    ----------
    ctx : invoke.Context
        The invoke context object.

    Notes
    -----
    This runs tests with coverage measurement and generates an HTML
    coverage report, **excluding** LLM tests (``@pytest.mark.llm``).
    LLM tests require human-in-the-loop operation and should not be
    included in automated coverage metrics.

    The report will be available in the htmlcov/ directory and can be
    opened in a browser for detailed analysis.

    See Also
    --------
    https://pytest-cov.readthedocs.io/
        Documentation for pytest-cov plugin.

    """
    cov_args = " ".join([f"--cov={pkg}" for pkg in SOURCE_PACKAGES])
    ctx.run(
        f'{PYTEST} -m "not llm" {cov_args} --cov-report=html',
        pty=USE_PTY,
    )
