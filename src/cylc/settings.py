import os
from pathlib import Path

HOME = Path.home()


########################
# PATHS
########################
CYLC_RUN = HOME / "cylc-run"
CYLC_SRC = HOME / "cylc-src"

########################
# EXECUTION
########################
CYLC_RESUME = False
CYLC_OVERWRITE = False
CYLC_EXTEND = False

########################
# MISC
########################
CYLC_DEFAULT_RUN_NAME = "exp"
CYLC_CONDA_ENV = os.getenv("$CYLC_CONDA", "cylcenv")

# this is the file name where to declare cylc workflow
CYLC_WORKFLOW = "flow.cylc"
