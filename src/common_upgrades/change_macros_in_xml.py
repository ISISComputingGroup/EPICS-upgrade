import os
import re
from xml.parsers.expat import ExpatError

from src.common_upgrades.utils.constants import FILTER_REGEX, CONFIG_FOLDER, COMPONENT_FOLDER, IOC_FILE


class ChangeMacrosInXML(object):
    """
    Changes macros in XML files.
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

    def change_macro(self, ioc_name, macros_to_change):
        """
        Changes macros in all xml files that contain the correct macros (name and possibly value) for a specified ioc.

        Args:
            ioc_name: Name of the IOC to change macros within.
            macros_to_change: List of 2-tuples of old_macro and new_macro Macro classes.
        Returns:
            None.
        """

        for path, ioc_xml in self.ioc_file_generator():
            for ioc in self.ioc_tag_generator(path, ioc_xml, ioc_name):
                macros = ioc.getElementsByTagName("macros")[0]
                for old_macro, new_macro in macros_to_change:
                    for macro in macros.getElementsByTagName("macro"):
                        self._change_macro_name(macro, old_macro.name, new_macro.name)
                        self._change_macro_value(macro, old_macro.value, new_macro.value)

            self._file_access.write_xml_file(path, ioc_xml)

    def ioc_file_generator(self):
        """
        Generator giving all the IOC files in all configurations.

        Yields:
            Tuple: The path to the ioc file and it's xml representation.
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
            path: Path to the xml file
            ioc_xml: Ioc_xml tag
            ioc_to_change: Name of the ioc to change.

        Yields:
            ioc: Ioc xml tag.
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

        Returns:
            None.
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

