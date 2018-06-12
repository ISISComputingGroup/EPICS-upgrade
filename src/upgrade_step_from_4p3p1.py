from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
import re

from .common_upgrades.xml_config_filter import XMLConfig
from .common_upgrades.config_filter import GlobalsConfig

class UpgradeStepFrom4p3p1(UpgradeStep):
    """
    Change the PIMOT macros from BAUD1 and PORT1 to BAUD and PORT respectively.
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        return self.change_pimot_macros(file_access, logger)


    def change_pimot_macros(self, file_access, logger):
        """
        Change the PIMOT macros from BAUD1 and PORT1 to BAUD and PORT respectively.

        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        config_filter = ConfigFilter(file_access, logger)
        macro_change1 = {
            "ioc_name": "PIMOT",
            "current_name": "BAUD1",
            "new_name" : "BAUD"
        }

        try:
            xml_config = XMLConfig(file_access, logger)
            xml_config.change_macro(macro_change1)

            global_config = GlobalsConfig(file_access, logger)
            global_config.macro_change(macro_change1)
            global_config.write_modified_globals_file()

        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1
        return 0
