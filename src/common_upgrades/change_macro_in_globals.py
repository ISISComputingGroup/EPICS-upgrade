import re
from src.common_upgrades.utils.constants import GLOBALS_FILENAME, FILTER_REGEX


class ChangeMacroInGlobals(object):
    """
    An interface to replace arbitrary macros in a globals.txt file
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
        Loads in a globals file as a list of strings.

        Returns:
            Globals file loaded as list of strings if globals file exists.
            Empty list otherwise.
        """

        if self._file_access.exists(GLOBALS_FILENAME):
            return self._file_access.open_file(GLOBALS_FILENAME)
        else:
            return []

    def change_macro(self, ioc_name, old_macro, new_macro):
        """
        Changes the macro name and possibly value in the globals.txt file for a given IOC.

        Args:
            ioc_name: Name of the IOC
            old_macro: Old Macro objects to be changed.
            new_macro: New Macro object for the macro to be changed to.

        Returns:
            None
        """

        for index in self._globals_filter_generator(ioc_name):
            self._apply_regex_macro_change(ioc_name, old_macro, new_macro, index)

        self.write_modified_globals_file()

        return None

    def _globals_filter_generator(self, ioc_to_change):
        """
        Returns lines containing specified IOCs from globals.txt

        Generator that gives all the lines for a given IOC in globals.txt.
        This will match IOCs with the same name as the root plus any that have a number
        appended in the form _XX.

        Args:
            ioc_to_change: the root name of the ioc to change

        Yields:
            Index that the ioc is on.
        """
        for index, line in enumerate(self._loaded_file if self._loaded_file is not None else []):
            if line.startswith("{}_".format(ioc_to_change)):
                self._logger.info("Found line '{}' in {}".format(line, GLOBALS_FILENAME))
                yield index

    def _determine_replacement_values(self, old_macro, new_macro):
        """
        Determines whether to change just the macro name, just the macro value or both given the fields
        entered in the provided dictionary

        Args:
            old_macro
            new_macro
        Returns:
            regex_changes: Dictionary of regex representations of the strings to search for/replace.

        """

        if old_macro.value is None:
            old_value_search = r".*"

            if new_macro.value is None:
                new_value_replacement = r"\3"
            else:
                new_value_replacement = new_macro.value
        else:
            old_value_search = old_macro.value
            new_value_replacement = new_macro.value

        regex_changes = {'old_macro_search': old_macro.name,
                         'new_macro_replacement': new_macro.name,
                         'old_value_search': old_value_search,
                         'new_value_replacement': new_value_replacement}

        return regex_changes

    def _apply_regex_macro_change(self, ioc_name, old_macro, new_macro, line_number):
        """
        Applies a regular expression to modify a macro.

        Args:

        Returns:
            None
        """

        regex_args = self._determine_replacement_values(old_macro, new_macro)

        replace_regex = re.compile(r"({}_\d\d__)({})=({})".format(ioc_name, regex_args["old_macro_search"],
                                                                  regex_args["old_value_search"]))

        self._loaded_file[line_number] = re.sub(replace_regex, r"\1{}={}".format(regex_args["new_macro_replacement"],
                                                                                 regex_args["new_value_replacement"]),
                                                self._loaded_file[line_number])

    def write_modified_globals_file(self):
        """
        Writes the modified globals file to disc

        Returns:
            None

        """
        self._file_access.write_file(GLOBALS_FILENAME, self._loaded_file)
