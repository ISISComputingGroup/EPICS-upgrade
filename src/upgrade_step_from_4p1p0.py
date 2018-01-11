from src.file_access import FileAccess
from src.local_logger import LocalLogger
from src.common_upgrades.config_filter import ConfigFilter
from src.upgrade_step import UpgradeStep
from enum import Enum
import re
import os
from xml.dom import minidom

MTRCTRL_STR = "MTRCTRL"
MTRCTRL_XML = """<macro name="MTRCTRL" pattern="^[0-9]{{1,2}}$" description="Controller number used in motor address assignment" value="{}"/>"""

GALIL_ADDR_STR = "GALILADDR"
GALIL_ADDR_XML = """<macro name="GALILADDR" pattern="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$" description="IP address of Galil controller (MTR01* PVs)" value="{}"/>"""

OLD_ADDR_MACRO_REGEX = r'GALILADDR([\d]{2})'

GALIL_FOLDER = os.path.join("configurations", "galil")

CMD_REGEX = r'.+\.cmd$'
GALIL_CMD_REGEX = r'galil([\d]{1,2})\.cmd$'

OLD_IOC_EXISTS_MACRO_REGEX = r'\$\(IFDMC([\d]{2})\)'
NEW_IOC_EXISTS_MACRO_REGEX = r'$(IFIOC_GALIL_\1)'


class UpgradedState(Enum):
    INVALID = -1
    UPGRADABLE = 0
    UPGRADED = 1


class UpgradeStepFrom4p1p0(UpgradeStep):
    """
    Change the Galil macros from:
        GALILADDR0X = IP
    to:
        GALILADDR = IP
        MTRCTRL = X
    and:
        $(IFDMC01)
    to:
        $(IFIOC_GALIL_01)

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
        ret_val = self.change_ioc_macros(file_access, logger)
        if ret_val == 0:
            logger.info("Finished changing macros, now modifying galil.cmd files")
            ret_val = self.change_cmd_files(file_access, logger)
        return ret_val

    def change_cmd_files(self, file_access, logger):
        """
        Changes the galilX.cmd files in the following way:
            Renamed to galilXX.cmd
            Change references to GALILADDRXX to GALILADDR as above
        Changes all *.cmd files to:
            $(IFDMC01) -> $(IFIOC_GALIL_01)
        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        dirs = file_access.listdir(GALIL_FOLDER)
        for filename in dirs:
            if re.search(CMD_REGEX, filename):
                try:
                    cmd_lines = file_access.open_file(filename)
                except IOError as e:
                    logger.error("Cannot open {}".format(filename))
                    return -3

                # Replace IF_IOC_MACRO, keeping the filename the same
                new_filename = filename
                cmd_lines = [re.sub(OLD_IOC_EXISTS_MACRO_REGEX, NEW_IOC_EXISTS_MACRO_REGEX, line) for line in cmd_lines]

                # If the file is a galil.cmd do additional changes
                is_galil_cmd = re.search(GALIL_CMD_REGEX, filename)
                if is_galil_cmd:
                    cmd_lines = [re.sub(OLD_ADDR_MACRO_REGEX, GALIL_ADDR_STR, line) for line in cmd_lines]
                    logger.info("Modifying GALILADDR in {}".format(filename))

                    new_filename = os.path.join(GALIL_FOLDER, "galil{:02d}.cmd".format(int(is_galil_cmd.group(1))))

                # Save the cmd file
                try:
                    file_access.write_file(new_filename, cmd_lines)
                    logger.info("Saving {}".format(new_filename))
                    if filename != new_filename:
                        logger.info("Removing {}".format(filename))
                        file_access.remove_file(filename)
                except IOError as e:
                    logger.error("Cannot save {} and remove {}".format(new_filename, filename))
                    return -4
        return 0

    def _are_macros_upgradable(self, macro_xml, logger):
        """
        Checks whether the macros in the current file are in a state where they can be easily upgraded.

        Args:
            macro_xml (NodeList): List of the macro nodes
        Returns:
            An UpgradedState telling you the state of the macros
        """
        macro_names = [m.getAttribute("name") for m in macro_xml]

        contains_mtrctrl = MTRCTRL_STR in macro_names
        contains_new_galiladdr = "GALILADDR" in macro_names
        old_macros = [m for m in macro_names if re.match(OLD_ADDR_MACRO_REGEX, m)]

        if contains_new_galiladdr and contains_mtrctrl and not any(old_macros):
            logger.info("IOC already contains GALILADDR and {}".format(MTRCTRL_STR))
            return UpgradedState.UPGRADED

        if len(old_macros) > 1:
            logger.error("IOC controls multiple GALILs")
            return UpgradedState.INVALID

        if any(old_macros) and not contains_mtrctrl and not contains_new_galiladdr:
            return UpgradedState.UPGRADABLE

        if len(old_macros) == 0:
            logger.info("IOC contains no address")
            return UpgradedState.UPGRADED

        logger.error("IOC contains invalid mix of versions")
        return UpgradedState.INVALID

    def _add_node_and_whitespace(self, parent_xml, new_xml, whitespace):
        """
        Adds a node and some whitespace to xml.
        Args:
            parent_xml (Node): node to add to
            new_xml (str): new xml to add
            whitespace (str): the whitespace to add
        """
        parent_xml.appendChild(minidom.parseString(new_xml).firstChild)
        parent_xml.appendChild(parent_xml.ownerDocument.createTextNode(whitespace))

    def _change_macros(self, macros_xml):
        """
        Changes the macros in the given xml.
        Args:
            macros_xml (NodeList): the current macros
        """
        macro_names = [m for m in macros_xml.getElementsByTagName("macro")]
        old_macro = [m for m in macro_names
                     if re.match(OLD_ADDR_MACRO_REGEX, m.getAttribute("name"))][0]

        old_galil_num = re.match(OLD_ADDR_MACRO_REGEX, old_macro.getAttribute("name")).group(1)
        old_galil_ip = old_macro.getAttribute("value")

        self._add_node_and_whitespace(macros_xml, MTRCTRL_XML.format(old_galil_num), "\n\t\t\t")
        self._add_node_and_whitespace(macros_xml, GALIL_ADDR_XML.format(old_galil_ip), "\n\t\t")

        macros_xml.removeChild(old_macro.nextSibling)  # Remove the whitespace before the old macro
        macros_xml.removeChild(old_macro)

    def change_ioc_macros(self, file_access, logger):
        """
        Change the Galil macros from:
            GALILADDRXX = IP
        to:
            GALILADDR = IP
            MTRCTRL = X

        Args:
            file_access (FileAccess): file access
            logger (Logger): logger
        """
        config_filter = ConfigFilter(file_access, logger)
        try:
            for ioc in config_filter.ioc_filter_generator("GALIL"):
                macros_xml = ioc.getElementsByTagName("macros")[0]
                upgrade_state = self._are_macros_upgradable(macros_xml.getElementsByTagName("macro"), logger)
                if upgrade_state is UpgradedState.UPGRADABLE:
                    self._change_macros(macros_xml)
                elif upgrade_state is UpgradedState.INVALID:
                    return -1
        except Exception as e:
            logger.error("Changing macros failed: {}".format(str(e)))
            return -2
        return 0
