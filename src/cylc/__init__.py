import importlib
import logging
import os
from pathlib import Path
from typing import Dict, Any

import yaml

CYLC_PACKAGE_PATH = Path(__file__).parent
DEFAULT_CYLC_CONFIG = CYLC_PACKAGE_PATH / "config" / "default_config.yaml"
logger = logging.getLogger("medfs")
_CFG = None

_imports = {
    "CylcEngine": "src.cylc.engine.CylcEngine",
    "cylc_util": "src.cylc.util",
}


def get_config() -> Dict[str, Any]:
    global _CFG
    if _CFG is None:
        cylc_config = Path(os.getenv("CYLC_CONFIG", DEFAULT_CYLC_CONFIG))
        logger.debug(f"CYLC_CONFIG={CYLC_PACKAGE_PATH}")
        with cylc_config.open() as config:
            _CFG = yaml.safe_load(config)
    return _CFG


# Dynamical import
globals().update(
    {
        name: importlib.import_module(module.rsplit(".", 1)[0]).__dict__[
            module.rsplit(".", 1)[1]
        ]
        for name, module in _imports.items()
    }
)
