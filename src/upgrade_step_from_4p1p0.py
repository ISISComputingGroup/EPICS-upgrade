from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
import re
from xml.dom import minidom

MTRCTRL_STR = "MTRCTRL"
MTRCTRL_XML = """<macro name="MTRCTRL" pattern="^[0-9]{{1,2}}$" description="Controller number used in motor address assignment" value="{}"/>"""

GALIL_ADDR_STR = "GALILADDR"
GALIL_ADDR_XML = """<macro name="GALILADDR" pattern="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$" description="IP address of Galil controller (MTR01* PVs)" value="{}"/>"""

OLD_MACROS_REGEX = "^GALILADDR([\d]{2})$"


class UpgradeStepFrom4p1p0(UpgradeStep):
    """
    Change the Galil macros from:
        GALILADDR0X = IP
    to:
        GALILADDR = IP
        MTRCTRL = X

    Change file galilX.cmd to be called galil0X.cmd
    Change references to GALILADDR0X in the galilX.cmd to GALILADDR as above
    """

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        self.change_ioc_macros(file_access, logger)

    def _are_current_macros_upgradable(self, macros, old_macros, logger):
        """
        Args:
            macros (list): List of the current macro name
            old_macros (list): List of the old macros in the xml
        Returns:
            bool: True if current macros are upgradable
        """
        contains_mtrctrl = MTRCTRL_STR in macros
        contains_new_galiladdr = "GALILADDR" in macros

        if contains_new_galiladdr and contains_mtrctrl and not any(old_macros):
            logger.info("IOC already contains GALILADDR and {}".format(MTRCTRL_STR))
            return False

        if len(old_macros) > 1:
            logger.error("IOC controls multiple GALILs")
            return False

        if any(old_macros) and not contains_mtrctrl and not contains_new_galiladdr:
            return True

        logger.error("IOC contains invalid mix of versions")
        return False

    def change_ioc_macros(self, file_access, logger):
        """
        Change the Galil macros from:
            GALILADDRXX = IP
        to:
            GALILADDR = IP
            MTRCTRL = X

        Args:
            file_access (FileAccess): file access
        """
        config_filter = ConfigFilter(file_access, logger)
        for ioc in config_filter.ioc_filter_generator("GALIL"):
            macros_xml = ioc.getElementsByTagName("macros")[0]
            macro_xml_list = macros_xml.getElementsByTagName("macro")
            old_macros = [m for m in macro_xml_list if re.match(OLD_MACROS_REGEX, m.getAttribute("name"))]
            macro_names = [m.getAttribute("name") for m in macro_xml_list]
            if self._are_current_macros_upgradable(macro_names, old_macros, logger):
                old_galil_num = re.match(OLD_MACROS_REGEX, old_macros[0].getAttribute("name")).group(1)
                old_galil_ip = old_macros[0].getAttribute("value")

                macros_xml.appendChild(minidom.parseString(MTRCTRL_XML.format(old_galil_num)).firstChild)
                # add some formatting to make it look nice
                macros_xml.appendChild(macros_xml.ownerDocument.createTextNode("\n\t\t\t"))
                macros_xml.appendChild(minidom.parseString(GALIL_ADDR_XML.format(old_galil_ip)).firstChild)
                # add some formatting to make it look nice
                macros_xml.appendChild(macros_xml.ownerDocument.createTextNode("\n\t\t"))

                macros_xml.removeChild(old_macros[0].nextSibling)  # Remove the whitespace before the old macro
                macros_xml.removeChild(old_macros[0])
