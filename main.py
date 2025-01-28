#!/usr/bin/env python

import logging
import os
from pathlib import Path

import click

ROOT_DIR = Path(__file__).parent.resolve()
HOME_DIR = Path.home()
logger = logging.getLogger("medfs")
logger.setLevel(logging.INFO)


########################
# CYLC CONFIGURATION
########################
CYLC_CONFIGURATION = {}


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
