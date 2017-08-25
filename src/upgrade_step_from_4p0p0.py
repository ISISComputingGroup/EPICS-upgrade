from src.common_upgrades import RenameOPIInSynoptics
from src.upgrade_step import UpgradeStep
from file_access import FileAccess


from local_logger import LocalLogger


class UpgradeStepFrom4p0p0(UpgradeStep):
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
        return RenameOPIInSynoptics("Beamstop", "XY Beam-stop").perform(file_access, logger)
