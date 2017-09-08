from file_access import FileAccess
from local_logger import LocalLogger
from src.common_upgrades.add_to_base_iocs import AddToBaseIOCs
from src.common_upgrades.synoptics import Synoptics
from src.upgrade_step import UpgradeStep

XML_TO_ADD = """\
    <ioc autostart="true" name="ARACCESS" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
"""


class UpgradeStepFrom3p2p1p1(UpgradeStep):
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
        if AddToBaseIOCs("ARACCESS", "ALARM", XML_TO_ADD).perform(file_access, logger) != 0:
            return 1
        elif Synoptics().update_paths(file_access, logger,
                                    [()]
                                    ) != 0:
            return 2
        else:
            return 0
        return
