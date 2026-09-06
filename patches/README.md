Although we try to use official sources for dependencies, sometimes the official
sources don't support a platform (especially mobile platforms), or there's a bug
fix/feature that is required to support Pillow's usage.

This folder contains patches that must be applied to official sources, organized
by the platforms that need those patches.

Each patch is against the root of the unpacked official tarball, and is named by
appending `.patch` to the end of the tarball that is to be patched. This
includes the full version number; so if the version is bumped, the patch will
at a minimum require a filename change.

Wherever possible, these patches should be contributed upstream, in the hope that
future Pillow versions won't need to maintain these patches.
