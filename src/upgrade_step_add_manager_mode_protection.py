from src.upgrade_step import UpgradeStep
from file_access import FileAccess
from local_logger import LocalLogger
from src.common_upgrades.utils.constants import CONFIG_FOLDER
from src.common_upgrades.utils.constants import COMPONENT_FOLDER

import os
from io import open
import xml.etree.ElementTree as ET


class UpgradeStepAddManagerModeProtection(UpgradeStep):
    """
    An upgrade step that adds the isProtected boolean element to the meta.xml for a configuration.
    """

    def perform(self, file_access, logger):
        """
        Change meta.xml configuration schema to have isProtected element

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success

        """

        for folder in os.walk(CONFIG_FOLDER):
            self._add_isProtected_to_meta_in_folders(folder)
        for folder in os.walk(COMPONENT_FOLDER):
            self._add_isProtected_to_meta_in_folders(folder)
        return 0

    def _add_isProtected_to_meta_in_folders(self, folder):
        try:
            file = folder[0] + "\meta.xmlb"
            meta_xml = ET.parse(file)
            if len(meta_xml.getroot().findall('isProtected')) == 0:
                protected_tag = ET.SubElement(meta_xml.getroot(), 'isProtected')
                protected_tag.text = 'false'
                meta_xml.write(file)
        except IOError as e:
            print("IOError: {}".format(e))
