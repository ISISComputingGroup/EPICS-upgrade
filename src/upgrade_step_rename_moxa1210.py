import os
import traceback

import six

from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML

from src.upgrade_step import UpgradeStep


class UpgradeMOXA1210IOCs(UpgradeStep):
    """
    Renames the moxa1210 IOC to the more general moxa12xx
    """

    def perform(self, file_access, logger):
        """
        Change macros pointing to MOXA1210 to from BAUD1 and PORT1 to BAUD and PORT respectively.

        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        ioc_name = "MOXA1210"
        new_ioc_name = "MOXA12XX"

        try:
            change_xml_macros = ChangeMacrosInXML(file_access, logger)
            change_xml_macros.change_ioc_name(ioc_name, new_ioc_name)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        try:
            change_global_macros = ChangeMacroInGlobals(file_access, logger)
            change_global_macros.change_ioc_name(ioc_name, new_ioc_name)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        try:
            change_global_macros = ChangeMacrosInXML(file_access, logger)
            change_global_macros.change_ioc_name_in_synoptics(ioc_name, new_ioc_name)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        return 0
