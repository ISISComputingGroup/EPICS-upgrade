from xml.dom import minidom
from xml.parsers.expat import ExpatError

from src.file_access import FileAccess
from src.local_logger import LocalLogger


class ChangeIOCMacros():
    """
    Changes the macros for a given IOC.
    """

    def __init__(self, file_access, ioc_to_change):
        """
        Constructs a dictionary of all the iocs that will need changing.
        Args:
            file_access (FileAccess): file access.
            ioc_to_change (str): the name of the ioc to change.
        """
        self._ioc_to_change = ioc_to_change
        self.iocs_in_configs = self._filter_iocs(file_access)

    def _filter_iocs(self, file_access):
        """
        Finds all the configurations with the given IOC.

        Args:
            file_access (FileAccess): file access.

        Returns:
            dictionary: The configuration and the associated xml.
        """
        found_iocs = dict()
        for config, ioc_xml in file_access.ioc_file_generator:
            for ioc in ioc_xml.getElementsByTagName("ioc"):
                if ioc.getAttribute("name") == self._ioc_to_change:
                    found_iocs[config] = ioc_xml
        return found_iocs

    def replace_macros(self, old_macro_name):
        pass




