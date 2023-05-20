import sys

from setuptools.build_meta import *  # noqa: F401, F403
from setuptools.build_meta import _BuildMetaBackend


class _CustomBuildMetaBackend(_BuildMetaBackend):
    def run_setup(self, setup_script="setup.py"):
        if self.config_settings:
            flags = []
            for key in ("enable", "disable", "vendor"):
                settings = self.config_settings.get(key)
                if settings:
                    if not isinstance(settings, list):
                        settings = [settings]
                    for value in settings:
                        flags.append("--" + key + "-" + value)
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
