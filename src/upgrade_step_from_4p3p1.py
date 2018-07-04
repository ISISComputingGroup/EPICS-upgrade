from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
import os

from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep


class UpgradeStepFrom4p3p1(UpgradeStep):
    """
    Change the PIMOT macros from BAUD1 and PORT1 to BAUD and PORT respectively.
    """

    def perform(self, file_access, logger):
        """
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail
        """
        filename = os.path.join("configurations", "banner.xml")
        file_contents = ["""<?xml version="1.0" ?>
<banner xmlns="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:blk="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
<items>
 <item>
  <name>Manager mode</name>
  <pv>CS:MANAGER</pv>
  <local>true</local>
 </item>
 </items>
</banner>
"""]

        file_access.write_file(filename, file_contents)
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
        ioc_name = "PIMOT"
        macros_to_change = [
            (Macro("BAUD1"), Macro("BAUD")),
            (Macro("PORT1"), Macro("PORT"))
        ]

        try:
            change_xml_macros = ChangeMacrosInXML(file_access, logger)
            change_xml_macros.change_macros(ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1

        try:
            change_global_macros = ChangeMacroInGlobals(file_access, logger)
            change_global_macros.change_macros(ioc_name, macros_to_change)

        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1

        return 0
