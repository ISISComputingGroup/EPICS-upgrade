import os
import xml.etree.ElementTree as ET

from src.common_upgrades.utils.constants import COMPONENT_FOLDER, CONFIG_FOLDER
from src.upgrade_step import UpgradeStep


class UpgradeStepAddMetaXmlElement(UpgradeStep):
    """An upgrade step that adds a passed element to the meta.xml for a configuration."""

    def __init__(self, tag, tag_value):
        self.tag = tag
        self.tag_value = tag_value
        super(UpgradeStepAddMetaXmlElement, self).__init__()

    def perform(self, file_access, logger):
        """Change meta.xml configuration schema to have self.tag element

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success

        """
        for folder in os.walk(CONFIG_FOLDER):
            if CONFIG_FOLDER != folder[0]:
                if self._add_tag_to_meta_in_folders(folder, logger) != 0:
                    return -1
        for folder in os.walk(COMPONENT_FOLDER):
            if COMPONENT_FOLDER != folder[0]:
                if self._add_tag_to_meta_in_folders(folder, logger) != 0:
                    return -1
        return 0

    def _add_tag_to_meta_in_folders(self, folder, logger):
        try:
            meta_file_path = os.path.join(folder[0] + r"\meta.xml")
            meta_xml = ET.parse(meta_file_path)
            if len(meta_xml.getroot().findall(self.tag)) == 0:
                xml_tag = ET.SubElement(meta_xml.getroot(), self.tag)
                xml_tag.text = self.tag_value
                meta_xml.write(meta_file_path)
        except IOError as e:
            logger.error("IOError: {}".format(e))
            return -1

        return 0
