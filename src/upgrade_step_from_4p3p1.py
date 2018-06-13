from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.upgrade_step import UpgradeStep
import re


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

    @staticmethod
    def _change_macros(macros_xml):
        """
        Changes the macros in the given xml.
        Args:
            macros_xml (NodeList): the current macros
        """
        for m in macros_xml.getElementsByTagName("macro"):
            name = m.getAttribute("name")
            if name.endswith("1"):
                m.setAttribute("name", name[:-1])

    def change_pimot_macros(self, file_access, logger):
        """
        Change the PIMOT macros from BAUD1 and PORT1 to BAUD and PORT respectively.

        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        macros_to_change = [
            {
                "ioc_name": "PIMOT",
                "old_macro": ("BAUD1", None),
                "new_macro": ("BAUD", None)
            },
            {
                "ioc_name": "PIMOT",
                "old_macro": ("PORT1", None),
                "new_macro": ("PORT", None)
            }
        ]
        try:
            change_global_macros = ChangeMacroInGlobals(file_access, logger)
            change_xml_macros = ChangeMacrosInXML(file_access, logger)

            change_xml_macros.change_macro(macros_to_change)

        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1
        return 0
