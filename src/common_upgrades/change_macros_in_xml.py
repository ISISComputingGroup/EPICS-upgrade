import os
from xml.parsers.expat import ExpatError
import re

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class ChangeMacrosInXML(object):
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

    def change_macro(self, macro_changes):
        """
        Changes macros in all xml files that contain the correct macros for a specified ioc.

        Args:
            macro_changes: list with entries which are dictionaries with fields
                ioc_name: name of the ico
                old_macro: (old_macro_name , old_value): macro to be changed and value to be changed
                new_macro: (new_macro_name, new_value): macro to be changed to and value to be changed to
        """

        for path, ioc_xml in self.ioc_file_generator():
            for macro_change in macro_changes:
                for ioc in self.ioc_tag_generator(path, ioc_xml, macro_change["ioc_name"]):
                    macros = ioc.getElementsByTagName("macros")[0]
                    for macro in macros.getElementsByTagName("macro"):
                        self._change_macro_name(macro, macro_change["old_macro"][0], macro_change["new_macro"][0])
                        self._change_macro_value(macro, macro_change["old_macro"][1], macro_change["new_macro"][1])

            self._file_access.write_xml_file(path, ioc_xml)

    def ioc_file_generator(self):
        """
        Generator giving all the IOC files in all configurations.

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

    def ioc_tag_generator(self, path, ioc_xml, ioc_to_change):
        """
        Generator giving all the IOC tags in all configurations.

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
    def _change_macro_name(macro, old_macro_name, new_macro_name):
        """
        Changes the macros in the given xml.

        Args:
            macro : The macro node to change.
            old_macro_name: The macro name to change.
            new_macro_name: The macro name to be set.
        """
        name = macro.getAttribute("name")
        if re.match(old_macro_name, name) is not None:
            macro.setAttribute("name", new_macro_name)

    @staticmethod
    def _change_macro_value(macro, old_macro_value, new_macro_value):
        """
        Changes the macros in the given xml.
        Args:
            macro : The macro node to change.
            old_macro_value: The macro value to change.
            new_macro_value: The macro value to be set.
        Returns:
            None: If old_macro_value is None.
        """
        if old_macro_value is not None:
            value = macro.getAttribute("value")
            if re.match(old_macro_value, value) is not None:
                macro.setAttribute("value", new_macro_value)
        else:
            return None

