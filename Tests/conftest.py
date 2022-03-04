import io


def pytest_report_header(config):
    try:
        from PIL import features

        with io.StringIO() as out:
            features.pilinfo(out=out, supported_formats=False)
            return out.getvalue()
    except Exception as e:
        return f"pytest_report_header failed: {e}"


def pytest_configure(config):
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
