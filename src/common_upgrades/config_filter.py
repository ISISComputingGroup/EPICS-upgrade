import os
from xml.parsers.expat import ExpatError
import re

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.join("configurations", "globals.txt")

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class GlobalsConfig(object):
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
        self._loaded_file = self.load_globals_file()

    def load_globals_file(self):
        """
        loads in a globals file as a list of strings

        Returns:
            Globals file loaded as list of strings

        """

        if self._file_access.exists(GLOBALS_FILENAME):
            return self._file_access.open_file(GLOBALS_FILENAME)

    def macro_change(self, macro_change):
        """
        Modifies the macro change held within the class. All changes after this is called
        will be performed with the updated macro change.

        Args:
            macro_change: Dict-like. Contains the regular expression representation of the
            macro before and after the change.

        Returns:
            None

        """
        assert isinstance(macro_change, dict)

        for index in self._globals_filter_generator(macro_change["ioc_name"]):
            self._apply_regex_macro_change(index)

        return None

    def _globals_filter_generator(self, ioc_to_change):
        """
        Generator that gives all the lines for a given IOC in globals.txt and saves them back to their original location
        after they've been yielded. This will match IOCs with the same name as the root plus any that have a number
        appended in the form _XX. To change the line change the yielded lines[index] to the value given.

        Args:
            ioc_to_change: the root name of the ioc to change
        """

        for index, line in enumerate(self._loaded_file):
            if line.startswith("{}_".format(ioc_to_change)):
                self._logger.info("Found line '{}' in {}".format(line, GLOBALS_FILENAME))
                yield index

    def _apply_regex_macro_change(self, line_number):
        """
        Applies a regular expression to modify a macro.

        Returns:

        """

        replace_regex = r"({})_\d\d__)({})=(.*)".format(self._macro_change["ioc_name"], self._macro_change["current_state"])

        macro_change = re.compile(replace_regex)
        self._loaded_file[line_number] = re.sub(macro_change, r"\1{}\3".format(self._macro_change["new_state"]), self._loaded_file[line_number])
        return None

    def write_modified_globals_file(self):
        """
        Writes the modified globals file to disc

        Returns:
            None

        """

        self._file_access.write_file(GLOBALS_FILENAME, self._loaded_file)