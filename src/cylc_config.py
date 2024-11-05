import os
from pathlib import Path

DEFAULT_RESUME = False
DEFAULT_OVERWRITE = False
DEFAULT_EXTEND = False
CYLC_SRC_FLOW_NAME = "flow.cylc"


def cylc_run() -> Path:
    """Cylc run path"""
    return Path(os.environ["CYLC_RUN_DIR"])


def cylc_src() -> Path:
    """Cylc src path"""
    return Path(os.environ["CYLC_SRC_DIR"])
