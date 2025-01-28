#!/usr/bin/env python

import logging
import shutil
import subprocess
import time
from pathlib import Path

from cylc import get_config
from cylc.util import increase_index_in_str_by_one

logger = logging.getLogger("medfs")


class CylcEngine:
    def __init__(
        self,
        workflow_cfg: Path,
        **cfg
    ):
        self.flow_cylc = workflow_cfg

        # load and get cylc configuration
        self.cfg = get_config(**cfg)

        self.installed_run_name = None

    @property
    def workflow_name(self):
        return self.flow_cylc.stem

    @property
    def id(self) -> str:
        return f"{self.workflow_name}/{self.cfg.CYLC_RUN_NAME}"

    @property
    def path_to_contact(self) -> Path:
        """Path to contact file (special sem file used by cylc itself)"""
        return self.cfg.CYLC_RUN / self.id / ".service" / "contact"

    @property
    def cylc_run_directory(self) -> Path:
        return self.cfg.CYLC_RUN / self.id

    @property
    def cylc_src_workflow_directory(self) -> Path:
        """Path to workflow directory in cylc-src"""
        return self.cfg.CYLC_SRC / self.workflow_name

    @property
    def cylc_src_workflow(self) -> Path:
        """Path to workflow installed in cylc-src path"""
        return self.cylc_src_workflow_directory / self.cfg.CYLC_WORKFLOW

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
        return self.cylc_run_directory.exists()

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
        shutil.rmtree(self.cylc_src_workflow_directory, ignore_errors=True)

    def link_flow_to_cylc_src(self) -> None:
        cylc_src_wf = self.cylc_src_workflow
        try:
            cylc_src_wf.parent.mkdir(parents=True, exist_ok=True)
            cylc_src_wf.symlink_to(self.flow_cylc)
            logger.info(f"Linked {self.flow_cylc} to {cylc_src_wf}")
        except FileExistsError:
            if cylc_src_wf.samefile(self.flow_cylc):
                return
            msg = f"Workflow conflicts\n\t- Installed: {cylc_src_wf}\n\t- Current: {self.flow_cylc}"
            logger.error(msg)
            raise ValueError(msg)

    def install_workflow(self) -> None:
        if self.cfg.CYLC_RESUME:
            self.path_to_contact.unlink(missing_ok=True)
            return

        if self.cfg.CYLC_OVERWRITE:
            self.stop_and_clean()

        if self.id_exist():
            raise ValueError(f"Workflow already exists: {self.id}")

        self.link_flow_to_cylc_src()
        self.install()

    def get_run_name_to_install(self) -> str:
        """Determine the final run name to be installed"""
        if self.cfg.CYLC_EXTEND:
            return self.run_name_extension()
        return self.cfg.CYLC_RUN_NAME

    def run_name_extension(self) -> str:
        """Extend the latest run name available:
        - if exp is available return exp1
        - if expX is available return expX+1
        """
        workflow_run_path = self.cfg.CYLC_RUN / self.workflow_name
        run_directories = sorted(
            [f for f in workflow_run_path.glob(f"{self.cfg.CYLC_RUN_NAME}*")]  # noqa: C416
        )
        try:
            # Increase index of latest element
            last_run = sorted(run_directories)[-1]
            return increase_index_in_str_by_one(last_run.name)
        except IndexError:
            # If no previous run, return the default one
            return self.cfg.CYLC_RUN_NAME
