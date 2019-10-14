from src.upgrade_step import UpgradeStep
from src.common_upgrades.utils.constants import CONFIG_FOLDER
from src.common_upgrades.utils.constants import COMPONENT_FOLDER

import os
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
            if (CONFIG_FOLDER != folder[0]):
                if (self._add_isProtected_to_meta_in_folders(folder, logger)  != 0):
                    return -1
        for folder in os.walk(COMPONENT_FOLDER):
           if (COMPONENT_FOLDER != folder[0]):
               if (self._add_isProtected_to_meta_in_folders(folder, logger) != 0):
                   return -1
        return 0


    def _add_isProtected_to_meta_in_folders(self, folder, logger):
        try:
            meta_file_path = os.path.join(folder[0] + "\meta.xml")
            meta_xml = ET.parse(meta_file_path)
            if len(meta_xml.getroot().findall('isProtected')) == 0:
                protected_tag = ET.SubElement(meta_xml.getroot(), 'isProtected')
                protected_tag.text = 'false'
                meta_xml.write(meta_file_path)
        except IOError as e:
            logger.error("IOError: {}".format(e))
            return -1

        return 0
