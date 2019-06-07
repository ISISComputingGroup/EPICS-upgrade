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

    def change_pv_name(self, old_pv_name, new_pv_name):
        """
        Replaces all instances of old_pv_name with new_pv_name in an XML tree
        Args:
            old_pv_name: String, the old pv name
            new_pv_name: String, The desired new pv name

        Returns:
            None
        """
        for path, block_xml in self._file_access.get_config_files(BLOCK_FILE):
            for block in block_xml.getElementsByTagName("block"):
                current_pv = block.getElementsByTagName("read_pv")[0]
                if current_pv.firstChild.nodeType != current_pv.TEXT_NODE:
                    continue
                current_pv_value = current_pv.firstChild.nodeValue
                if old_pv_name in current_pv_value:
                    replacement = current_pv_value.replace(old_pv_name, new_pv_name)
                    current_pv.firstChild.replaceWholeText(replacement)

            self._file_access.write_xml_file(path, block_xml)

