#!/usr/bin/env python

import logging
import re
import shutil
import subprocess
import time
from pathlib import Path

from src import cylc_config as cfg

logger = logging.getLogger("medfs")
STR_INDEX = re.compile("\d+$")


class CylcEngine:
    def __init__(
        self,
        flow: Path,
        run_name: str,
        resume: bool = cfg.DEFAULT_RESUME,
        overwrite: bool = cfg.DEFAULT_OVERWRITE,
        extend: bool = cfg.DEFAULT_EXTEND,
    ):
        self.flow = flow
        self.run_name = run_name
        self.resume = resume
        self.overwrite = overwrite
        self.extend = extend

        self.installed_run_name = None

    @property
    def workflow_name(self):
        return self.flow.stem

    @property
    def id(self) -> str:
        return f"{self.workflow_name}/{self.run_name}"

    @property
    def contact_path(self) -> Path:
        """Path to contact file (special sem file used by cylc itself)"""
        return cfg.cylc_run() / ".service" / "contact"

    def exec(self, cmd: str, opt: str, ignore: bool = False) -> None:
        """

        Args:
            cmd: Cylc command (i.e. validate, install, stop, play,...)
            opt: Cylc options
            ignore: Doesn't exit in case of error in cmd execution
        """
        cylc_cmd = f"cylc {cmd} {self.id}"
        if opt is not None:
            cylc_cmd += f" {opt}"

        print(f"Executing: {cylc_cmd}")
        result = subprocess.run(
            cylc_cmd, stdout=None, stderr=None, text=True, shell=True
        )
        try:
            result.check_returncode()
        except subprocess.CalledProcessError:
            logger.critical(f"Exit code not zero: {result.returncode}")
            if not ignore:
                exit(1)

    def id_exist(self) -> bool:
        return (cfg.cylc_run() / self.id).exists()

    def stop(self) -> None:
        self.exec("stop", ignore=True)
        # usually cylc stop return immediately, but it takes some seconds to be effective
        time.sleep(3)

    def clean(self):
        if not self.id_exist():
            return
        self.exec("clean")

    def install(self):
        """Install run name and if necessary update run name"""
        self.installed_run_name = self.get_run_name_to_install()
        self.exec("install", opt=f"--run-name {self.installed_run_name}")

    def play(self):
        self.exec("play")

    def cylc_src_workflow_base_path(self) -> Path:
        """Path to workflow directory in cylc-src"""
        return cfg.cylc_src() / self.workflow_name

    def cylc_src_workflow(self) -> Path:
        """Path to workflow installed in cylc-src path"""
        return self.cylc_src_workflow_base_path() / cfg.CYLC_SRC_FLOW_NAME

    def stop_and_clean(self):
        self.stop()
        self.clean()
        shutil.rmtree(self.cylc_src_workflow_base_path(), ignore_errors=True)

    def link_flow_to_cylc_src(self):
        cylc_src_wf = self.cylc_src_workflow()
        try:
            cylc_src_wf.symlink_to(self.flow)
        except FileExistsError:
            if cylc_src_wf.samefile(self.flow):
                return
            msg = f"Workflow conflicts\n\t- Installed: {cylc_src_wf}\n\t- Current: {self.flow}"
            raise ValueError(msg)

    def install_workflow(self) -> None:
        if self.resume:
            # to resume a stopped cylc workflow is only necessary to remove contact file
            self.contact_path.unlink(missing_ok=True)
            return

        if self.overwrite:
            self.stop_and_clean()

        if self.id_exist():
            raise ValueError(f"Workflow already exists: {self.id}")

        self.link_flow_to_cylc_src()
        self.install()

    def get_run_name_to_install(self):
        """Determine the final run name to be installed"""
        if self.extend:
            return self.run_name_extension()
        return self.run_name

    def run_name_extension(self):
        """Extend the latest run name available:
        - if exp is available return exp1
        - if expX is available return expX+1
        """
        workflow_run_path = cfg.cylc_run() / self.workflow_name
        run_directories = sorted(
            [f for f in workflow_run_path.glob(f"{self.run_name}*")]
        )
        try:
            # Increase index of latest element
            last_run = sorted(run_directories)[-1]
            return increase_index_in_str(last_run.name)
        except IndexError:
            # If no previous run, return the default one
            return self.run_name


def increase_index_in_str(s: str) -> str:
    """Given a string like expX, return expY, where Y = X + 1"""
    try:
        index = int(STR_INDEX.findall(s)[0])
    except IndexError:
        index = 0

    return s.replace(s, str(index + 1))
