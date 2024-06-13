from __future__ import annotations
import pytest
import sys

pytest_plugins = ["Tests.helper"]
test_name = None


branch_coverage1 = {
    "1": False,
    "2": False,
    "3": False,
}

branch_coverage2 = {
    "1": False,
    "2": False,
    "3": False,
    "4": False,
    "5": False,
}


def calculate_coverage(test_name):
    coverage_data = {
        "test_image_rotate": branch_coverage1,
        "test_imageshow": branch_coverage2,
    }

    if test_name not in coverage_data:
        print(f"No coverage data for test {test_name}")
        return

    num_branches = len(coverage_data[test_name])
    covered_branches = sum(value is True for value in coverage_data[test_name].values())

    coverage = (covered_branches/num_branches) * 100
    print(f"\nbranches for {test_name}:", num_branches, "\n")
    print(f"\nbranches covered for {test_name}:", covered_branches, "\n")
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