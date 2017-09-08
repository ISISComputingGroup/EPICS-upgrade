from file_access import FileAccess
from local_logger import LocalLogger
from src.common_upgrades.synoptics import Synoptics
from src.upgrade_step import UpgradeStep
from data.target_details_release_4p0p0 import OPI_PATH_KEYS


class UpgradeStepFrom3p2p1p2(UpgradeStep):
    """
    Add the Alarm server to the _base ioc so that it autostarts
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        return Synoptics().update_opi_paths(file_access, logger, OPI_PATH_KEYS)
