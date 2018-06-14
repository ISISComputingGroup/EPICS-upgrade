import os
from xml.parsers.expat import ExpatError
import re

CONFIG_FOLDER = os.path.join("configurations", "configurations")
COMPONENT_FOLDER = os.path.join("configurations", "components")
IOC_FILE = "iocs.xml"
GLOBALS_FILENAME = os.path.join("configurations", "globals.txt")

# Matches an ioc name and it's numbered IOC's e.g. GALIL matches GALIL_01, GALIL_02
FILTER_REGEX = "^{}(_[\d]{{2}})?$"


class ChangeMacroInGlobals(object):
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

    def apply_macro_change(self, macro_change):
        """
        Applies a macro change given a dicionary containing the IOC name, old macro and new macros. All changes after
        this is called will be performed with the updated macro change.

        Args:
            macro_change: Dict-like or list-of-dicts. Contains fields ioc_name : the IOC name,
                                                                      old_macro: (old_macro_name, old_macro_value)
                                                                      new_macro: (new_macro_name, new_macro_value)

        Returns:
            None

        """

        if not type(macro_change) == list:
            macro_change = [macro_change, ]

        for macro in macro_change:
            macro = self._sanitise_input_dictionary_tuples(macro)

            for index in self._globals_filter_generator(macro["ioc_name"]):
                self._apply_regex_macro_change(macro, index)

        self.write_modified_globals_file()

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

    def _dict_field_to_tuple(self, dict_field):
        """
        Converts a string to a 1-tuple containing that string, or returns a 1- or 2-tuple input
        Args:
            dict_field: A string to be contained in a 1-tuple, or a tuple

        Returns:
            field_as_tuple: tuple representation of dict_field, if it is not already a tuple
        """

        if type(dict_field) is not tuple:
            field_as_tuple = (dict_field,)
        else:
            field_as_tuple = dict_field

        return field_as_tuple

    def _sanitise_input_dictionary_tuples(self, macro_change):
        """

        Args:
            macro_change: A dict-like object containing three fields:
            ioc_name : the IOC name,
            old_macro: old_macro_name or 2-tuple of (old_macro_name, old_macro_value)
            new_macro: new_macro_name or 2-tuple of (new_macro_name, new_macro_value)

        Returns:
            sanitised_macro_change: A dict-like object containing three fields:
            ioc_name : the IOC name,
            old_macro: tuple of (old_macro_name,) or (old_macro_name, old_macro_value)
            new_macro: tuple of (new_macro_name) or (new_macro_name, new_macro_value)


        """
        sanitised_macro_change = macro_change.copy()

        sanitised_macro_change["new_macro"] = self._dict_field_to_tuple(macro_change["new_macro"])
        sanitised_macro_change["old_macro"] = self._dict_field_to_tuple(macro_change["old_macro"])

        return sanitised_macro_change

    def _determine_filled_fields(self, macro):
        """
        Returns whether the both the macro name and values are set, or just the macro name

        Args:
            macro: 1- or 2-tuple containing a macro name, or a macro name and value

        Returns:
            macro_name: String containing the macro name
            macro_value: None or String containing the macro value

        """

        if (len(macro)) == 1:
            # Name change only
            macro_name = macro[0]
            macro_value = None
        elif(len(macro)) == 2:
            # Name and/or value change
            macro_name = macro[0]
            macro_value = macro[1]
        else:
            raise AssertionError("Invalid input dict")

        return macro_name, macro_value

    def _copy_macro_name_if_only_one_is_defined(self, old_name, new_name):
        """
        If only the new or old name is defined, return the same name for each.

        Args:
            old_name: None or String containing the original name of the macro
            new_name: None or String containing the new name of the macro

        Returns:
            old_name: String containing the old name, or the new name if it was not originally defined
            new_name String containing the new name, or the old name if it was not originally defined

        Raises AssertionError: If neither name is defined (both None)

        """

        if new_name is None and old_name is None:
            raise AssertionError("Must provide a macro name")
        elif old_name is None:
            return new_name, new_name
        elif new_name is None:
            return old_name, old_name
        else:
            return old_name, new_name

    def _determine_replacement_values(self, macro_change):
        """
        Determines whether to change just the macro name, just the macro value or both given the fields
        entered in the provided dictionary

        Args:
            macro_change: A dict-like object containing three fields:
            ioc_name : the IOC name,
            old_macro: (old_macro_name, old_macro_value (optional))
            new_macro: (new_macro_name, new_macro_value (optional))

        Returns:
            regex_changes: The regex representations of the strings to search for/replace

        """

        old_macro_name, old_macro_value = self._determine_filled_fields(macro_change["old_macro"])
        new_macro_name, new_macro_value = self._determine_filled_fields(macro_change["new_macro"])

        old_macro_name, new_macro_name = self._copy_macro_name_if_only_one_is_defined(old_macro_name, new_macro_name)

        if old_macro_value is None and new_macro_value is None:
            # Regex search/replace for original values
            old_value_search = r".*"
            new_value_replacement = r"\3"

        elif new_macro_value is not None and old_macro_value is None:
            # Search all, replace with new value
            old_value_search = r".*"
            new_value_replacement = new_macro_value

        else:
            # Search for old value, replace with new value
            old_value_search = old_macro_value
            new_value_replacement = new_macro_value

        regex_changes = {'old_macro_search': old_macro_name,
                         'new_macro_replacement': new_macro_name,
                         'old_value_search': old_value_search,
                         'new_value_replacement': new_value_replacement}

        return regex_changes

    def _apply_regex_macro_change(self, macro_change, line_number):
        """
        Applies a regular expression to modify a macro.

        Returns:
            None
        """

        regex_args = self._determine_replacement_values(macro_change)

        replace_regex = re.compile(r"(%s_\d\d__)(%s)=(%s)" %(macro_change["ioc_name"],
                                                             regex_args["old_macro_search"],
                                                             regex_args["old_value_search"]))

        self._loaded_file[line_number] = re.sub(replace_regex, r"\1{}={}".format(regex_args["new_macro_replacement"],
                                                                           regex_args["new_value_replacement"]),
                                                                           self._loaded_file[line_number])
        return None

    def write_modified_globals_file(self):
        """
        Writes the modified globals file to disc

        Returns:
            None

        """

        self._file_access.write_file(GLOBALS_FILENAME, "\n".join(self._loaded_file))
