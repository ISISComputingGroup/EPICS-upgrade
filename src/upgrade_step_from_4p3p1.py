from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
import re
from xml.dom import minidom


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
        config_filter = ConfigFilter(file_access, logger)
        try:
            for ioc in config_filter.ioc_filter_generator("PIMOT"):
                macros_xml = ioc.getElementsByTagName("macros")[0]
                self._change_macros(macros_xml)
        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1
        return 0
