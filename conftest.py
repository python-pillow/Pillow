pytest_plugins = ["Tests.helper"]


def pytest_configure(config):
    """
    Keep a reference to pytest's configuration in our helper class.
    This function is called by pytest each time the configuration is updated.
    https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_configure
    """
    import Tests.helper

    Tests.helper.pytestconfig = config
