import os
from pathlib import Path

DEFAULT_RESUME = False
DEFAULT_OVERWRITE = False
DEFAULT_EXTEND = False
CYLC_SRC_FLOW_NAME = "flow.cylc"


def get_conda_env():
    return os.environ["CYLC_CONDA_ENV"]


def cylc_run() -> Path:
    """Cylc run path"""
    return Path(os.environ["CYLC_RUN_DIR"])


def cylc_src():
    """Cylc src path"""
    return os.environ["CYLC_SRC_DIR"]


def get_cylc_default_run_name():
    return os.environ["CYLC_DEFAULT_RUN_NAME"]


def get_cylc_wf_dir():
    return os.environ["CYLC_WF_DIR"]
