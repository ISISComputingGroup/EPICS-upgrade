import logging

import git

from src.common_upgrades.utils.constants import CALIB_FOLDER
from src.file_access import FileAccess
from src.git_utils import RepoFactory
from src.upgrade_step import UpgradeStep


class UpgradeFrom25p2p1(UpgradeStep):
    """
    Update calibrations repo to use new (gitlab) remote.
    """
    def perform(self, file_access: FileAccess, logger: logging.Logger) -> int:
        repo: git.Repo = RepoFactory.get_repo(CALIB_FOLDER)
        repo.remote("origin").set_url("https://gitlab.stfc.ac.uk/isisexperimentcontrols/common.git")
        return 0
