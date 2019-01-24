import traceback

import six

from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML

from src.common_upgrades.utils.macro import Macro

from src.upgrade_step import UpgradeStep


class UpgradeMOXA1210IOCs(UpgradeStep):
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
        old_ioc_name = "MOXA1210"
        new_ioc_name = "MOXA12XX"

        macros_to_change = [
            (Macro("CHAN00NAME"), Macro("CHAN0NAME")),
            (Macro("CHAN01NAME"), Macro("CHAN1NAME")),
            (Macro("CHAN02NAME"), Macro("CHAN2NAME")),
            (Macro("CHAN03NAME"), Macro("CHAN3NAME")),
            (Macro("CHAN04NAME"), Macro("CHAN4NAME")),
            (Macro("CHAN05NAME"), Macro("CHAN5NAME")),
            (Macro("CHAN06NAME"), Macro("CHAN6NAME")),
            (Macro("CHAN07NAME"), Macro("CHAN7NAME")),
            (Macro("CHAN08NAME"), Macro("CHAN8NAME")),
            (Macro("CHAN09NAME"), Macro("CHAN9NAME")),
        ]

        try:
            change_xml_macros = ChangeMacrosInXML(file_access, logger)

            change_xml_macros.change_ioc_name(old_ioc_name, new_ioc_name)

            change_xml_macros.change_macros(new_ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        try:
            change_global_macros = ChangeMacroInGlobals(file_access, logger)

            change_global_macros.change_ioc_name(old_ioc_name, new_ioc_name)

            change_global_macros.change_macros(new_ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        try:
            change_global_macros = ChangeMacrosInXML(file_access, logger)
            change_global_macros.change_ioc_name_in_synoptics(old_ioc_name, new_ioc_name)

        except Exception as e:
            logger.error("Changing MOXA1210 IOC name failed: {}".format(str(e)))
            traceback.print_exc()
            return -1

        return 0
