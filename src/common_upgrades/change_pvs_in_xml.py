from src.common_upgrades.utils.constants import BLOCK_FILE


class ChangePVsInXML(object):
    """Changes pvs in XML files."""

    def __init__(self, file_access, logger):
        """Initialise.

        Args:
            file_access: Object to allow for file access.
            logger: Logger to use.
        """
        self._file_access = file_access
        self._logger = logger

    def node_text_filter(self, filter_text, element_name, path, xml):
        """A generator that gives all the instances of filter_text within the element_name elements of the input_files.

        Args:
            filter_text: String, ext to find
            element_name: String, tag name of the elements where to look for filter_text
            path: Path to the xml to check
            xml: The contents of the xml

        Returns:
            Generator giving node instances
        """
        for node in xml.getElementsByTagName(element_name):
            if node.firstChild is None or node.firstChild.nodeType != node.TEXT_NODE:
                continue
            current_pv_value = node.firstChild.nodeValue
            if filter_text in current_pv_value:
                self._logger.info("{} found in {}".format(filter_text, path))
                yield node

    def _replace_text_in_elements(self, old_text, new_text, element_name, input_files):
        """Replaces all instances of old_text with new_text in all element_name elements of one or more XML files
        Args:
            old_text: String, old text to find
            new_text: String, new text to substitute
            element_name: String, tag name of the elements where to look for old_text
            input_files: Iterable, XML files where to substitute text
        """
        for path, xml in input_files:
            for node in self.node_text_filter(old_text, element_name, path, xml):
                replacement = node.firstChild.nodeValue.replace(old_text, new_text)
                node.firstChild.replaceWholeText(replacement)

            self._file_access.write_xml_file(path, xml)

    def change_pv_name(self, old_pv_name, new_pv_name):
        """Replaces all instances of old_pv_name with new_pv_name in the blocks config and all synoptics
        Args:
            old_pv_name: String, the old pv name
            new_pv_name: String, The desired new pv name

        """
        self.change_pv_name_in_blocks(old_pv_name, new_pv_name)
        self.change_pv_names_in_synoptics(old_pv_name, new_pv_name)

    def change_pv_name_in_blocks(self, old_pv_name, new_pv_name):
        """Move any blocks pointing at old_pv_name to point at new_pv_name.

        Args:
            old_pv_name: The old PV to remove references to
            new_pv_name: The new PV to replace it with
        """
        self._replace_text_in_elements(
            old_pv_name, new_pv_name, "read_pv", self._file_access.get_config_files(BLOCK_FILE)
        )

    def change_pv_names_in_synoptics(self, old_pv_name, new_pv_name):
        """Move any synoptic PV targets from pointing at old_pv_name to point to new_pv_name.

        Args:
            old_pv_name: The old PV to remove references to
            new_pv_name: The new PV to replace it with
        """
        self._replace_text_in_elements(
            old_pv_name, new_pv_name, "address", self._file_access.get_synoptic_files()
        )

    def get_number_of_instances_of_pv(self, pv_names):
        """Get the number of instances of a PV in the config and synoptic.

        Args:
            pv_names: String, a list of pvs to search for
        Return:
            The number of occurrences in both the config and the synoptic
        """
        num_of_instances = 0
        for pv_name in pv_names:
            for path, xml in self._file_access.get_config_files(BLOCK_FILE):
                num_of_instances += len(list(self.node_text_filter(pv_name, "read_pv", path, xml)))
            for path, xml in self._file_access.get_synoptic_files():
                num_of_instances += len(list(self.node_text_filter(pv_name, "address", path, xml)))

        return num_of_instances
