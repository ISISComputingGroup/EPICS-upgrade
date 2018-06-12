import os
from xml.parsers.expat import ExpatError
import re
from xml.dom import minidom

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.join("configurations", "globals.txt")

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class XMLConfig(object):
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

    def change_macro(self, macro_change):
        """
        Generator that gives all the IOCs with the given root IOC name and saves them back to their original location
        after they've been yielded. This will match IOCs with the same name as the root plus any that have a number
        appended in the form _XX.

        Args:
            macro_change: dictionary with
        """

        for path, ioc_xml in self._ioc_file_generator():

            for ioc in self._ioc_tag_generator(path, ioc_xml, macro_change["ioc_name"]):
                macros_xml = ioc.getElementsByTagName("macros")[0] # careful

                for macro in macros_xml.getElementsByTagName("macro"):
                    self._change_macro_name(macro, macro_change["current_name"], macro_change["new_name"])

            self._file_access.write_xml_file(path, ioc_xml)

    def _ioc_file_generator(self):
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

    def _ioc_tag_generator(self, path, ioc_xml, ioc_to_change):
        regex = re.compile(FILTER_REGEX.format(ioc_to_change))

        for ioc in ioc_xml.getElementsByTagName("ioc"):
            ioc_name = ioc.getAttribute("name")
            if regex.match(ioc_name):
                self._logger.info("Found {} in {}".format(ioc_name, path))
                yield ioc

    @staticmethod
    def _change_macro_name(macro, current_state, new_state):
        """
        Changes the macros in the given xml.
        Args:
            macros_xml (NodeList): the current macros
        """
        name = macro.getAttribute("name")
        if name == current_state:
            macro.setAttribute("name", new_state)
