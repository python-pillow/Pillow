import sys

from setuptools.build_meta import *  # noqa: F401, F403
from setuptools.build_meta import build_wheel

backend_class = build_wheel.__self__.__class__


class _CustomBuildMetaBackend(backend_class):
    def run_setup(self, setup_script="setup.py"):
        if self.config_settings:

            def config_has(key, value):
                settings = self.config_settings.get(key)
                if settings:
                    if not isinstance(settings, list):
                        settings = [settings]
                    return value in settings

            flags = []
            for dependency in (
                "zlib",
                "jpeg",
                "tiff",
                "freetype",
                "raqm",
                "lcms",
                "webp",
                "webpmux",
                "jpeg2000",
                "imagequant",
                "xcb",
            ):
                if config_has(dependency, "enable"):
                    flags.append("--enable-" + dependency)
                elif config_has(dependency, "disable"):
                    flags.append("--disable-" + dependency)
            for dependency in ("raqm", "fribidi"):
                if config_has(dependency, "vendor"):
                    flags.append("--vendor-" + dependency)
            if self.config_settings.get("platform-guessing") == "disable":
                flags.append("--disable-platform-guessing")
            if self.config_settings.get("debug") == "true":
                flags.append("--debug")
            if flags:
                sys.argv = sys.argv[:1] + ["build_ext"] + flags + sys.argv[1:]
        return super().run_setup(setup_script)

    def build_wheel(
        self, wheel_directory, config_settings=None, metadata_directory=None
    ):
        self.config_settings = config_settings
        return super().build_wheel(wheel_directory, config_settings, metadata_directory)


build_wheel = _CustomBuildMetaBackend().build_wheel
