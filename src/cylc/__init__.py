import importlib
import logging
from pathlib import Path

logger = logging.getLogger("medfs")
CYLC_PACKAGE_PATH = Path(__file__).parent
_CFG = None


SETTINGS_TO_LOAD = ["src.cylc.settings"]
_imports = {
    "CylcEngine": "src.cylc.engine.CylcEngine",
    "cylc_util": "src.cylc.util",
}


class Settings:
    def __init__(self, *modules, ext_settings=None):
        for module in modules:
            mod = importlib.import_module(module)
            for setting in dir(mod):
                if setting.isupper():
                    setattr(self, setting, getattr(mod, setting))
        if ext_settings is not None:
            self.configure(**ext_settings)

    def configure(self, **ext_settings):
        """Set new settings or override default ones."""
        for key, value in ext_settings.items():
            if key.isupper():
                setattr(self, key, value)


# lazy load of settings
def get_config(**kwargs) -> Settings:
    global _CFG
    if _CFG is None:
        _CFG = Settings(*SETTINGS_TO_LOAD)
    return _CFG


# Dynamical imports
globals().update(
    {
        name: importlib.import_module(module.rsplit(".", 1)[0]).__dict__[
            module.rsplit(".", 1)[1]
        ]
        for name, module in _imports.items()
    }
)
