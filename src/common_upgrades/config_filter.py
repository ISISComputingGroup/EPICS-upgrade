import os
from xml.parsers.expat import ExpatError

CONFIG_FOLDER = "configurations"
COMPONENT_FOLDER = "components"
IOC_FILE = "iocs.xml"


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
        config_root_paths = [os.path.join(self._config_base, f) for f in [COMPONENT_FOLDER, CONFIG_FOLDER]]
        for path in config_root_paths:
            for config in os.listdir(path):
                ioc_path = os.path.join(path, config, IOC_FILE)
                try:
                    yield (ioc_path, self._file_access.open_xml_file(ioc_path))
                except IOError:
                    self._logger.error("Cannot find {}".format(ioc_path))
                except ExpatError as ex:
                    self._logger.error("{} is invalid xml '{}'".format(path, ex))

    def ioc_filter_generator(self, ioc_to_change):
        """
        Generator that gives all the IOCs with the given name and saves them back to their original location
        after they've been yielded.

        Args:
            ioc_to_change: the name of the ioc to change
        """
        for path, ioc_xml in self.ioc_file_generator:
            for ioc in ioc_xml.getElementsByTagName("ioc"):
                if ioc.getAttribute("name") == ioc_to_change:
                    yield ioc
                    self._file_access.write_xml_file(path, ioc_xml)
