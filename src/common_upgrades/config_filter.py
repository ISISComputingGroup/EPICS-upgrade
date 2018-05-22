import os
from xml.parsers.expat import ExpatError
import re

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.join("configurations", "globals.txt")

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class ConfigFilter():
    """
    Filters configurations for specific things.
    """

    def __init__(self, file_access, logger):
        """
        Initialise.
        Args:
            file_access: object to allow for file access
            logger: Logger to use
        """
        self._file_access = file_access
        self._logger = logger

    def ioc_file_generator(self):
        """
        Generator giving all the IOC files in all the configurations.

        Yields:
            Tuple: The path to the ioc file and it's xml representation
        """
        for path in [COMPONENT_FOLDER, CONFIG_FOLDER]:
            for config in [c for c in self._file_access.listdir(path) if self._file_access.is_dir(c)]:
                ioc_path = os.path.join(config, IOC_FILE)
                try:
                    yield (ioc_path, self._file_access.open_xml_file(ioc_path))
                except IOError:
                    raise IOError("Cannot find {}".format(ioc_path))
                except ExpatError as ex:
                    raise ExpatError("{} is invalid xml '{}'".format(path, ex))

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

    def globals_filter_generator(self, ioc_to_change):
        """
        Generator that gives all the lines for a given IOC in globals.txt and saves them back to their original location
        after they've been yielded. This will match IOCs with the same name as the root plus any that have a number
        appended in the form _XX. To change the line change the yielded lines[index] to the value given.

        Args:
            ioc_to_change: the root name of the ioc to change
        """

        if self._file_access.exists(GLOBALS_FILENAME):
            line_changed = False
            lines = self._file_access.open_file(GLOBALS_FILENAME)
            for index, line in enumerate(lines):
                if line.startswith("{}_".format(ioc_to_change)):
                    self._logger.info("Found line '{}' in {}".format(line, GLOBALS_FILENAME))
                    line_changed = True
                    yield index, lines
            if line_changed:
                self._file_access.write_file(GLOBALS_FILENAME, lines)
