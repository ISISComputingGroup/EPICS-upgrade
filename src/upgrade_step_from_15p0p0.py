import logging
import os

from src.file_access import FileAccess
from src.upgrade_step import UpgradeStep
from src.common_upgrades.utils.constants import CONFIG_ROOT, EPICS_ROOT
from src.git_utils import RepoFactory
import git


CONTROLLERS = [
    "galil", "galilmul", "mclennan", "bkhoff_01", "linmot", "smc100_01", "sm300_01", "twincat"
]

# Unix timestamp of 2024/09/01 at midnight.
# This is the date when motor settings were copied. Commits more recent than this will not have
# been included in the copy, and therefore will have to be sorted out manually.
CUTOFF_TIMESTAMP = 1725145200

class UpgradeFrom15p0p0(UpgradeStep):
    """
    Remove motor settings
    """

    def perform(self, file_access: FileAccess, logger: logging.Logger):
        try:
            controller_dirs: list[str] = [os.path.join(CONFIG_ROOT, c) for c in CONTROLLERS]
            existent_controller_dirs: list[str] = [c for c in controller_dirs if os.path.exists(c)]

            for directory in existent_controller_dirs:
                logger.info(f"Checking for recent commits in {directory}")

                repo: git.Repo = RepoFactory.get_repo(directory)
                commit_timestamps: str = repo.git.log("--format=%ct", directory)

                integer_commit_timestamps: list[int] = [int(ts) for ts in commit_timestamps.split()]

                if any(ts > CUTOFF_TIMESTAMP for ts in integer_commit_timestamps):
                    motorext_path = os.path.join(
                        EPICS_ROOT,
                        "support",
                        "motorExtensions",
                        "master",
                        "settings",
                        "<instrument>"
                    )
                    raise ValueError(
                        "ERROR: Motor settings have changed since they were copied into "
                        "motorExtensions.\n\n"
                        f"The motor settings directories ({', '.join(CONTROLLERS)}) must be "
                        f"manually recopied from '{CONFIG_ROOT}' into '{motorext_path}', and then "
                        f"deleted from the settings repo. Ensure a pull request is created to "
                        f"update the version in the motorExtensions repository.\n\n"
                        f"Restart this upgrade script when complete. No directories have been "
                        f"altered yet."
                    )

            for directory in existent_controller_dirs:
                logger.info(f"Deleting {directory}")
                file_access.delete_folder(directory)

            return 0
        except Exception as e:
            logger.error("Unable to perform upgrade, caught error: {}".format(e))
            return 1
