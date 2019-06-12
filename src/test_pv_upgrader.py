from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML

from src.common_upgrades.utils.macro import Macro
from src.upgrade_step import UpgradeStep


class TestPVUpdater(UpgradeStep):
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

        pimot = self.change_pimot_macros(file_access, logger)
        PVs = self.change_block_PVs(file_access, logger)

        if pimot != 0 or PVs != 0:
            return -1
        else:
            return 0

        #self.pv_changer.change_pv_name(pv_to_change, new_pv)

        #return self.change_pimot_macros(file_access, logger)

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

    def change_block_PVs(self, file_access, logger):
        try:
            pv_changer = ChangePVsInXML(file_access, logger)
            pv_changer.change_pv_name('CHANGEME', 'CHANGED')
        except Exception as e:
            logger.error("Changing block PVs failed: {}".format(str(e)))
            return -1

        return 0

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
