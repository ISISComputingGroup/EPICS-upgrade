from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
import re
from xml.etree.ElementTree import SubElement


OLD_MACROS_REGEX = "^GALILADDR([\d]{2})$"

MTRCTRL_STR = "MTRCTRL"
MTRCTRL_PATTERN = ""
MTRCTRL_DESCRIPTION = ""


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

    def _are_current_macros_upgradable(self, macros, logger):
        """
        Args:
            macros (list): List of the current macro name
        Returns:
            bool: True if current macros are upgradable
        """
        contains_mtrctrl = MTRCTRL_STR in macros
        contains_new_galiladdr = "GALILADDR" in macros

        old_galiladdr = [re.match(OLD_MACROS_REGEX, m) for m in macros]

        if contains_new_galiladdr and contains_mtrctrl and not any(old_galiladdr):
            logger.info("IOC already contains GALILADDR and {}".format(MTRCTRL_STR))
            return False

        if len(old_galiladdr) > 1:
            logger.error("IOC controls multiple GALILs")
            return False

        if any(old_galiladdr) and not contains_mtrctrl and not contains_new_galiladdr:
            return True

        logger.error("IOC contains invalid mix of versions")
        return False

    def _create_MTRCTRL_macro(self, document, number):
        mtrctrl = document.createElement("macro")
        mtrctrl.setAttribute("name", MTRCTRL_STR)
        mtrctrl.setAttribute("value", number)
        mtrctrl.setAttribute("pattern", MTRCTRL_PATTERN)
        mtrctrl.setAttribute("description", MTRCTRL_DESCRIPTION)
        return mtrctrl

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
            macro_names = [m.getAttribute("name") for m in macros_xml.getElementsByTagName("macro")]
            if self._are_current_macros_upgradable(macro_names, logger):
                old_galil_num = [re.match(OLD_MACROS_REGEX, m) for m in macro_names][0].group(1)
                macros_xml.appendChild(self._create_MTRCTRL_macro(macros_xml.ownerDocument, old_galil_num))



