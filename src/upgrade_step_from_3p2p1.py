from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.common_upgrades.add_to_base_iocs import AddToBaseIOCs
from src.upgrade_step import UpgradeStep

XML_TO_ADD = """\
    <ioc autostart="true" name="ALARM" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
"""


class UpgradeStepFrom3p2p1(UpgradeStep):
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
        return AddToBaseIOCs("ALARM", "ISISDAE_01", XML_TO_ADD).perform(file_access, logger)
