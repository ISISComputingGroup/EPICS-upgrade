from src.common_upgrades.utils.constants import BLOCK_FILE


class ChangePVsInXML(object):
    """
    Changes pvs in XML files.
    """

    def __init__(self, file_access, logger):
        """
        Initialise.

        Args:
            file_access: Object to allow for file access.
            logger: Logger to use.
        """
        self._file_access = file_access
        self._logger = logger

    def _replace_text_in_elements(self, old_text, new_text, element_name, input_files):
        """
        Replaces all instances of old_text with new_text in all element_name elements of one or more XML files
        Args:
            old_text: String, old text to find
            new_text: String, new text to substitute
            element_name: String, tag name of the elements where to look for old_text
            input_files: Iterable, XML files where to substitute text

        Returns:
            The number of incidences found
        """
        number_found = 0
        for path, xml in input_files:
            for node in xml.getElementsByTagName(element_name):
                if node.firstChild.nodeType != node.TEXT_NODE:
                    continue
                current_pv_value = node.firstChild.nodeValue
                if old_text in current_pv_value:
                    number_found += 1
                    replacement = current_pv_value.replace(old_text, new_text)
                    node.firstChild.replaceWholeText(replacement)

            self._file_access.write_xml_file(path, xml)
        return number_found

    def change_pv_name(self, old_pv_name, new_pv_name):
        """
        Replaces all instances of old_pv_name with new_pv_name in the blocks config and all synoptics
        Args:
            old_pv_name: String, the old pv name
            new_pv_name: String, The desired new pv name

        Returns:
            The number of incidences found
        """
        number_found = self.change_pv_name_in_blocks(old_pv_name, new_pv_name)
        number_found += self.change_pv_names_in_synoptics(old_pv_name, new_pv_name)
        return number_found

    def change_pv_name_in_blocks(self, old_pv_name, new_pv_name):
        block_config = self._file_access.get_config_files(BLOCK_FILE)
        return self._replace_text_in_elements(old_pv_name, new_pv_name, "read_pv", block_config)

    def change_pv_names_in_synoptics(self, old_pv_name, new_pv_name):
        synoptics = self._file_access.get_synoptic_files()
        return self._replace_text_in_elements(old_pv_name, new_pv_name, "address", synoptics)
