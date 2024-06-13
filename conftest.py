from __future__ import annotations
import pytest

pytest_plugins = ["Tests.helper"]

branch_coverage1 = {
    "1": False,
    "2": False,
    "3": False,
}

def calculate_coverage():
    num_branches = len(branch_coverage1)
    covered_branches = sum(value is True for value in branch_coverage1.values())

    coverage = (covered_branches/num_branches) * 100

    return coverage

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    coverage = calculate_coverage()
    print("\nBRANCH COVERAGE:", coverage, "%\n")
