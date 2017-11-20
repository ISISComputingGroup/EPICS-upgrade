from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.common_upgrades.synoptics import Synoptics
from src.upgrade_step import UpgradeStep
from data.target_details_release_4p0p0 import OPI_PATH_KEYS as OPI_PATH_KEYS_4P0P0
from data.target_details_release_3p2p1 import OPI_PATH_KEYS as OPI_PATH_KEYS_3P2P1
from data.target_details_release_2p0p0 import OPI_PATH_KEYS as OPI_PATH_KEYS_2P0P0


class UpgradeStepFrom4p1p0(UpgradeStep):
    """
    Change the Galil macros from:
        GALILADDR0X = IP
    to:
        GALILADDR = IP
        MTRCTRL = X

    Change file galilX.cmd to be called galil0X.cmd
    Change references to GALILADDR0X in the galilX.cmd to GALILADDR as above
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """

    def change_ioc_macros(self, file_access):
        pass
