import os
from xml.parsers.expat import ExpatError
import re
from xml.dom import minidom

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class XMLMacroChanger(object):
    """
    Changes macros in XML files.
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
        Changes macros in all xml files that contain the
        Args:
            macro_change: dictionary with
        """

        for path, ioc_xml in self._ioc_file_generator():
            for ioc in self._ioc_tag_generator(path, ioc_xml, macro_change["ioc_name"]):
                macros = ioc.getElementsByTagName("macros")[0]
                for macro in macros.getElementsByTagName("macro"):
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
        """

        Args:
            path:
            ioc_xml:
            ioc_to_change:

        Yields:
            ioc: ioc xml tag
        """
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
