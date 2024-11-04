#!/usr/bin/env python

import os
from pathlib import Path

import click

ROOT_DIR = Path(__file__).parent.resolve()
HOME_DIR = Path.home()

########################
# CYLC CONFIGURATION
########################
CYLC_CONFIGURATION = {
    "CYLC_CONDA_ENV": "cylc",
    "CYLC_DEFAULT_RUN_NAME": "exp",
    "CYLC_RUN_DIR": HOME_DIR / "cylc-run",
    "CYLC_SRC_DIR": HOME_DIR / "cylc-src",
    "CYLC_WF_DIR": ROOT_DIR / "wf",
}


def export_to_env(k: str, v: str) -> None:
    """Equivalent to bash syntax: export k=v"""
    print(f"export {k}={v}")
    os.environ[k] = v


@click.group()
def main():
    print("Exporting cylc configuration:")
    for k, v in CYLC_CONFIGURATION.items():
        export_to_env(k, str(v))


@main.command()
def validate():
    pass


if __name__ == "__main__":
    main()
