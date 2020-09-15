from src.common_upgrades.utils.constants import BLOCK_FILE


def node_text_filter(filter_text, element_name, input_files):
    """
    A generator that gives all the instances of filter_text within the element_name elements of the input_files.
    Args:
        filter_text: String, ext to find
        element_name: String, tag name of the elements where to look for filter_text
        input_files: Iterable, XML files where to search

    Returns:
        Generator giving node instances
    """
    for path, xml in input_files:
        for node in xml.getElementsByTagName(element_name):
            if node.firstChild.nodeType != node.TEXT_NODE:
                continue
            current_pv_value = node.firstChild.nodeValue
            if filter_text in current_pv_value:
                yield node


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
        self.block_config = self._file_access.get_config_files(BLOCK_FILE)
        self.synoptics = self._file_access.get_synoptic_files()

    def _replace_text_in_elements(self, old_text, new_text, element_name, input_files):
        """
        Replaces all instances of old_text with new_text in all element_name elements of one or more XML files
        Args:
            old_text: String, old text to find
            new_text: String, new text to substitute
            element_name: String, tag name of the elements where to look for old_text
            input_files: Iterable, XML files where to substitute text
        """
        for node in node_text_filter(old_text, element_name, input_files):
            replacement = node.firstChild.nodeValue.replace(old_text, new_text)
            node.firstChild.replaceWholeText(replacement)

        for path, xml in input_files:
            self._file_access.write_xml_file(path, xml)

    def change_pv_name(self, old_pv_name, new_pv_name):
        """
        Replaces all instances of old_pv_name with new_pv_name in the blocks config and all synoptics
        Args:
            old_pv_name: String, the old pv name
            new_pv_name: String, The desired new pv name

        """
        self.change_pv_name_in_blocks(old_pv_name, new_pv_name)
        self.change_pv_names_in_synoptics(old_pv_name, new_pv_name)

    def change_pv_name_in_blocks(self, old_pv_name, new_pv_name):
        self._replace_text_in_elements(old_pv_name, new_pv_name, "read_pv", self.block_config)

    def change_pv_names_in_synoptics(self, old_pv_name, new_pv_name):
        self._replace_text_in_elements(old_pv_name, new_pv_name, "address", self.synoptics)

    def get_number_of_instances_of_pv(self, pv_names):
        """
        Get the number of instances of a PV in the config and synoptic.
        Args:
            pv_names: String, a list of pvs to search for
        Return:
            The number of occurrences in both the config and the synoptic
        """
        num_of_instances = 0
        for pv_name in pv_names:
            num_of_instances += len(node_text_filter(pv_name, "read_pv", self.block_config))
            num_of_instances += len(node_text_filter(pv_name, "address", self.synoptics))
        return num_of_instances
