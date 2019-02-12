import traceback

import six

from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML

from src.common_upgrades.utils.macro import Macro

from src.upgrade_step import UpgradeStep


class UpgradeMOXA12XXMacros(UpgradeStep):
    """
    Renames the moxa1210 IOC to the more general moxa12xx
    """

    def perform(self, file_access, logger):
        """
        Change ioc name MOXA1210 TO MOXA12XX. Remove leading zeroes in channel name macros

        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        ioc_name = "MOXA12XX"

        macros_to_change = [
            (Macro("IP_ADDR"), Macro("ADDR")),
        ]

        try:
            change_xml_macros = ChangeMacrosInXML(file_access, logger)

            change_xml_macros.change_macros(ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing MOXA12XX Macro failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        try:
            change_global_macros = ChangeMacroInGlobals(file_access, logger)

            change_global_macros.change_macros(ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing MOXA12XX Macro failed: {}".format(str(e)))
            traceback.print_exc()
            return -1
