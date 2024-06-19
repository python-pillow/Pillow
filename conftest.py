from __future__ import annotations
import pytest
import sys

from PIL import Image

pytest_plugins = ["Tests.helper"]


def calculate_coverage(test_name):
    branch = Image.branches
    branches = Image.branches
    num_branches = len(branches)
    branch_covered = {key: value for key, value in branches.items() if value is True}
    sum_branches = len(branch_covered)
    coverage = (sum_branches/num_branches) * 100
    print(f"\nBranches covered: {sum_branches}")
    print(f"\nTotal branches: {num_branches}")
    print("\nBRANCH COVERAGE:", coverage, "%\n")
    return coverage



@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    global test_name

    last_arg = sys.argv[-1]

    test_name = last_arg.split('/')[-1].split('::')[-1]

    test_name = test_name.rstrip('.py')

    return None

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    global test_name

    coverage = calculate_coverage(test_name)
    print("\nBRANCH COVERAGE for", test_name, ":", coverage, "%\n")

    