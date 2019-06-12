import re
from xml.parsers.expat import ExpatError

from src.common_upgrades.utils.constants import FILTER_REGEX, IOC_FILE, SYNOPTIC_FOLDER


def change_macro_name(macro, old_macro_name, new_macro_name):
    """
    Changes the macro name of a macro xml node.

    Args:
        macro : The macro node to change.
        old_macro_name: The macro name to change.
        new_macro_name: The macro name to be set.
    """
    name = macro.getAttribute("name")
    if re.match(old_macro_name, name) is not None:
        macro.setAttribute("name", new_macro_name)


def change_macro_value(macro, old_macro_value, new_macro_value):
    """
    Changes the macros in the given xml if a new macro value is given.

    Args:
        macro : The macro xml node to change.
        old_macro_value: The macro value to change.
        new_macro_value: The macro value to be set.
    """
    if new_macro_value is not None:
        value = macro.getAttribute("value")
        if old_macro_value is None:
            macro.setAttribute("value", new_macro_value)
        elif re.match(old_macro_value, value) is not None:
            macro.setAttribute("value", new_macro_value)


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

    def change_macros(self, ioc_name, macros_to_change):
        """
        Changes macros in all xml files that contain the correct macros for a specified ioc.

        Args:
            ioc_name: Name of the IOC to change macros within.
            macros_to_change: List of 2-tuples of old_macro and new_macro Macro classes.
        Returns:
            None.
        """

        for path, ioc_xml in self._file_access.get_config_files(IOC_FILE):
            for ioc in self.ioc_tag_generator(path, ioc_xml, ioc_name):
                macros = ioc.getElementsByTagName("macros")[0]
                for macro in macros.getElementsByTagName("macro"):
                    for old_macro, new_macro in macros_to_change:
                        change_macro_name(macro, old_macro.name, new_macro.name)
                        change_macro_value(macro, old_macro.value, new_macro.value)

            self._file_access.write_xml_file(path, ioc_xml)

    def change_ioc_name(self, old_ioc_name, new_ioc_name):
        """
        Replaces all instances of old_ioc_name with new_ioc_name in an XML tree
        Args:
            old_ioc_name: String, the old ioc prefix (without _XX number suffix)
            new_ioc_name: String, The desired new IOC prefix (without _XX number suffix)

        Returns:
            None
        """
        for path, ioc_xml in self._file_access.get_config_files(IOC_FILE):
            for ioc in ioc_xml.getElementsByTagName("ioc"):
                ioc_name_with_suffix = ioc.getAttribute("name")
                if old_ioc_name in ioc_name_with_suffix:
                    ioc_replacement = ioc_name_with_suffix.replace(old_ioc_name, new_ioc_name).upper()
                    ioc.setAttribute("name", ioc_replacement)

            self._file_access.write_xml_file(path, ioc_xml)

    def change_ioc_name_in_synoptics(self, old_ioc_name, new_ioc_name):
        """
        Replaces instances of old_ioc_name with new_ioc_name

        Args:
            old_ioc_name: String, the old ioc prefix (without _XX number suffix)
            new_ioc_name: String, The desired new IOC prefix (without _XX number suffix)

        Returns:
            None

        """
        path = SYNOPTIC_FOLDER

        for xml_path in [c for c in self._file_access.listdir(path) if c.endswith(".xml")]:
            try:
                synoptic_xml = self._file_access.open_xml_file(xml_path)
            except IOError:
                raise IOError("Cannot find {}".format(xml_path))
            except ExpatError as ex:
                raise ExpatError("{} is invalid xml '{}'".format(path, ex))

            for element in synoptic_xml.getElementsByTagName("value"):
                # Obtain text between the <value> tags (https://stackoverflow.com/a/317494 and https://stackoverflow.com/a/13591742)
                if element.firstChild is not None:
                    if element.firstChild.nodeType == element.TEXT_NODE:
                        ioc_name_with_suffix = element.firstChild.nodeValue

                        if old_ioc_name in ioc_name_with_suffix:
                            ioc_replacement = ioc_name_with_suffix.replace(old_ioc_name, new_ioc_name).upper()
                            element.firstChild.replaceWholeText(ioc_replacement)

            self._file_access.write_xml_file(xml_path, synoptic_xml)

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
