import os
from xml.parsers.expat import ExpatError
import re

CONFIG_FOLDER = "configurations"
COMPONENT_FOLDER = "components"
IOC_FILE = "iocs.xml"

FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class ConfigFilter():
    """
    Filters configurations for specific things.
    """

    def __init__(self, file_access, logger):
        self._file_access = file_access
        self._logger = logger

    def ioc_file_generator(self):
        """
        Generator giving all the IOC files in all the configurations.

        Yields:
            Tuple: The path to the ioc file and it's xml representation
        """
        for path in [COMPONENT_FOLDER, CONFIG_FOLDER]:
            for config in self._file_access.listdir(path):
                ioc_path = os.path.join(path, config, IOC_FILE)
                try:
                    yield (ioc_path, self._file_access.open_xml_file(ioc_path))
                except IOError:
                    self._logger.error("Cannot find {}".format(ioc_path))
                except ExpatError as ex:
                    self._logger.error("{} is invalid xml '{}'".format(path, ex))

    def ioc_filter_generator(self, ioc_to_change):
        """
        Generator that gives all the IOCs with the given root IOC name and saves them back to their original location
        after they've been yielded. This will match IOCs with the same name as the root plus any that have a number
        appended in the form _XX.

        Args:
            ioc_to_change: the root name of the ioc to change
        """
        regex = re.compile(FILTER_REGEX.format(ioc_to_change))

        for path, ioc_xml in self.ioc_file_generator():
            xml_changed = False
            for ioc in ioc_xml.getElementsByTagName("ioc"):
                ioc_name = ioc.getAttribute("name")
                if regex.match(ioc_name):
                    self._logger.info("Found {} in {}".format(ioc_name, path))
                    yield ioc
                    xml_changed = True
            if xml_changed:
                self._file_access.write_xml_file(path, ioc_xml)
