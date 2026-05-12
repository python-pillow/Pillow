from __future__ import annotations

import io
import sys
import sysconfig

import pytest

FREE_THREADED_BUILD = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

gil_enabled_at_start = True
if FREE_THREADED_BUILD:
    gil_enabled_at_start = sys._is_gil_enabled()  # type: ignore[attr-defined]


def pytest_report_header(config: pytest.Config) -> str:
    try:
        from PIL import features

        with io.StringIO() as out:
            features.pilinfo(out=out, supported_formats=False)
            return out.getvalue()
    except Exception as e:
        return f"pytest_report_header failed: {e}"


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter, exitstatus: int, config: pytest.Config
) -> None:
    if (
        FREE_THREADED_BUILD
        and not gil_enabled_at_start
        and sys._is_gil_enabled()  # type: ignore[attr-defined]
    ):
        tr = terminalreporter
        tr.ensure_newline()
        tr.section("GIL re-enabled", sep="=", red=True, bold=True)
        tr.line("The GIL was re-enabled at runtime during the tests.")
        tr.line("This can happen with no test failures if the RuntimeWarning")
        tr.line("raised by Python when this happens is filtered by a test.")
        tr.line("")
        tr.line("Please ensure all new C modules declare support for running")
        tr.line("without the GIL. Any new tests that intentionally imports")
        tr.line("code that re-enables the GIL should do so in a subprocess.")
        pytest.exit("GIL re-enabled during tests", returncode=1)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "pil_noop_mark: A conditional mark where nothing special happens",
    )

    # We're marking some tests to ignore valgrind errors and XFAIL them.
    # Ensure that the mark is defined
    # even in cases where pytest-valgrind isn't installed
    try:
        config.addinivalue_line(
            "markers",
            "valgrind_known_error: Tests that have known issues with valgrind",
        )
    except Exception:
        # valgrind is already installed
        pass
