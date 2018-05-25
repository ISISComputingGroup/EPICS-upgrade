import os
from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
import re


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
        config_filter = ConfigFilter(file_access, logger)
        try:
            for ioc in config_filter.ioc_filter_generator("PIMOT"):
                macros_xml = ioc.getElementsByTagName("macros")[0]
                self._change_macros(macros_xml)

            for line_index, iocs in config_filter.globals_filter_generator("PIMOT"):
                match = re.match(r"(PIMOT_\d\d__[^=]*)1(.*)", iocs[line_index])
                if match is not None:
                    iocs[line_index] = match.group(1) + match.group(2)

        except Exception as e:
            logger.error("Changing PIMOT macros failed: {}".format(str(e)))
            return -1
        return 0
