# Agent Instructions for Pillow

## What this project is

Pillow is the Python Imaging Library fork — a Python 3.10+ library for opening,
manipulating, and saving many image file formats. It is a mix of Python and C:
pure Python format plugins live in `src/PIL/`, and eight C extension modules
(`_imaging`, `_imagingcms`, `_imagingft`, `_imagingmath`, `_imagingmorph`,
`_imagingtk`, `_avif`, `_webp`) are compiled at install time via `setup.py`.

## Project layout

```
src/PIL/              Python source and C extension stubs (.pyi)
src/thirdparty/       Vendored C libraries (raqm, fribidi-shim, pythoncapi_compat)
Tests/                pytest test suite; Tests/helper.py has shared utilities
docs/                 Sphinx documentation (RST)
docs/releasenotes/    Per-release changelog entries
setup.py              C extension build configuration
_custom_build/        Custom setuptools build backend
src/PIL/_version.py   Version number (PEP 440)
pyproject.toml        Project metadata and optional dependency groups
.pre-commit-config.yaml  All linting and formatting hooks
```

## Install

```bash
python3 -m pip install -e ".[tests]"
```

The C extensions are compiled during install. Native libraries (libjpeg,
libpng, libtiff, libwebp, freetype2, littlecms2, etc.) must already be present
on the system.

## Test

```bash
python3 selftest.py          # quick sanity check
python3 -m pytest Tests/     # full test suite
python3 -m pytest Tests/ -n auto  # parallel (requires pytest-xdist)
```

Always run `python3 selftest.py` first. New features and bug fixes must include
tests. Test files follow the naming pattern `Tests/test_*.py`.

## Lint and format

```bash
make lint        # runs tox -e lint → pre-commit (black, ruff, clang-format,
                 #   bandit, sphinx-lint, pyproject-fmt, and more)
make lint-fix    # auto-fixes black and ruff violations
```

Or run pre-commit directly:

```bash
pre-commit run --all-files
```

All hooks must pass before a PR can be merged. Separate reformatting commits
from functional commits.

## Type checking

```bash
python3 -m tox -e mypy
```

## Documentation

Docs use Sphinx/RST. Build locally with `make doc`. Release notes go in
`docs/releasenotes/<version>.rst` using the existing section structure
(Security, Backwards incompatible changes, Deprecations, API changes, API
additions, Other changes). Use the `:cve:` RST role for CVE references.
Include a release note entry for any user-visible change.

## Pillow-specific guidance

Use `python3` and `python3 -m pip install` — never `python` or bare `pip`.

`Image.open()` takes a `formats=` argument (list/tuple of format IDs to
allowlist). There is no `format=` parameter.

`Image.OPEN` is an internal format registry. Do not recommend that users
mutate it as a security or configuration mechanism.

`pybind11` is a build-time-only dependency used for parallel C compilation,
not for C++/Python bindings.

Use fully qualified exception names: `Image.DecompressionBombError` and
`Image.DecompressionBombWarning`, not the bare class names.

Do not embed specific numeric values for thresholds like `MAX_IMAGE_PIXELS` —
they may be changed by the user at runtime. Reference the named constant instead.
