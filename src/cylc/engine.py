#!/usr/bin/env python

import logging
import shutil
import subprocess
import time
from pathlib import Path

from src.cylc import get_config
from src.cylc.util import increase_index_in_str_by_one

logger = logging.getLogger("medfs")


class CylcEngine:
    def __init__(
        self,
        flow: Path,
        run_name: str,
        **cfg
    ):
        self.flow = flow
        self.run_name = run_name

        # load and get cylc configuration
        self.cfg = get_config(**cfg)

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
        return self.cfg.CYLC_RUN / self.id / ".service" / "contact"

    @property
    def workflow_run_path(self) -> Path:
        return self.cfg.CYLC_RUN / self.id

    @property
    def cylc_src_workflow_base_path(self) -> Path:
        """Path to workflow directory in cylc-src"""
        return self.cfg.CYLC_SRC / self.workflow_name

    @property
    def cylc_src_workflow(self) -> Path:
        """Path to workflow installed in cylc-src path"""
        return self.cylc_src_workflow_base_path / self.cfg.CYLC_WORKFLOW

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
        return self.workflow_run_path.exists()

    def stop(self) -> None:
        """Wrapper to 'cylc stop' command + a sleep time to wait cylc"""
        self.exec("stop", ignore=True)
        # usually cylc stop return immediately, but it takes some seconds to be effective
        time.sleep(3)

    def clean(self):
        """Wrapper to 'cylc clean' command"""
        if not self.id_exist():
            return
        self.exec("clean")

    def install(self):
        """Install run name and if necessary update run name"""
        self.installed_run_name = self.get_run_name_to_install()
        self.exec("install", opt=f"--run-name {self.installed_run_name}")

    def play(self):
        """Wrapper to 'cylc play' command"""
        self.exec("play")

    def stop_and_clean(self):
        self.stop()
        self.clean()
        shutil.rmtree(self.cylc_src_workflow_base_path, ignore_errors=True)

    def link_flow_to_cylc_src(self) -> None:
        cylc_src_wf = self.cylc_src_workflow
        try:
            cylc_src_wf.parent.mkdir(parents=True, exist_ok=True)
            cylc_src_wf.symlink_to(self.flow)
        except FileExistsError:
            if cylc_src_wf.samefile(self.flow):
                return
            msg = f"Workflow conflicts\n\t- Installed: {cylc_src_wf}\n\t- Current: {self.flow}"
            raise ValueError(msg)

    def install_workflow(self) -> None:
        if self.cfg.CYLC_RESUME:
            # to resume a stopped cylc workflow is only necessary to remove contact file
            self.contact_path.unlink(missing_ok=True)
            return

        if self.cfg.CYLC_OVERWRITE:
            self.stop_and_clean()

        if self.id_exist():
            raise ValueError(f"Workflow already exists: {self.id}")

        self.link_flow_to_cylc_src()
        self.install()

    def get_run_name_to_install(self):
        """Determine the final run name to be installed"""
        if self.cfg.CYLC_EXTEND:
            return self.run_name_extension()
        return self.run_name

    def run_name_extension(self):
        """Extend the latest run name available:
        - if exp is available return exp1
        - if expX is available return expX+1
        """
        workflow_run_path = self.cfg.CYLC_RUN / self.workflow_name
        run_directories = sorted(
            [f for f in workflow_run_path.glob(f"{self.run_name}*")]
        )
        try:
            # Increase index of latest element
            last_run = sorted(run_directories)[-1]
            return increase_index_in_str_by_one(last_run.name)
        except IndexError:
            # If no previous run, return the default one
            return self.run_name
