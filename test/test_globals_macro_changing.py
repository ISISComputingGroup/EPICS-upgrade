import unittest
from hamcrest import assert_that
from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from test.mother import LoggingStub, FileAccessStub, EXAMPLE_GLOBALS_FILE
import os
from src.common_upgrades.utils.macro import Macro
from src.common_upgrades.utils.constants import GLOBALS_FILENAME


class TestFindingIOC(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.file_access.existing_files = {GLOBALS_FILENAME: GLOBALS_FILENAME}
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacroInGlobals(self.file_access, self.logger)

    def test_that_WHEN_asked_to_load_globals_file_THEN_the_default_globals_file_is_loaded(self):
        result = self.macro_changer.load_globals_file()

        reference = EXAMPLE_GLOBALS_FILE.split("\n")

        assert_that(result, reference)

    def test_that_GIVEN_globals_file_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_are_returned(self):
        ioc_to_change = "CHANGE_ME"

        matching_indices = []
        for index in self.macro_changer._globals_filter_generator(ioc_to_change):
            matching_indices.append(index)

        self.assertEqual(len(matching_indices), 0)

    def test_that_GIVEN_globals_file_with_requested_iocs_WHEN_filtering_THEN_the_expected_ioc_is_returned(self):
        ioc_to_change = "BINS"

        matching_indices = []
        matched_lines = []
        for index in self.macro_changer._globals_filter_generator(ioc_to_change):
            matching_indices.append(index)
            matched_lines.append(self.macro_changer._loaded_file[index])

        self.assertEqual(len(matching_indices), 1)
        self.assertIn("BINS", matched_lines[0])


class TestChangingMacro(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.file_access.existing_files = {GLOBALS_FILENAME: GLOBALS_FILENAME}
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacroInGlobals(self.file_access, self.logger)

    def test_that_GIVEN_globals_file_with_old_macro_THEN_all_old_macros_are_changed(self):
        ioc_to_change = "GALOL"
        macros_to_change = [
            (Macro("CHANGEME"), Macro("CHANGED"))
        ]

        self.macro_changer.change_macros(ioc_to_change, macros_to_change)

        testfile = EXAMPLE_GLOBALS_FILE.replace("CHANGEME",
                                                "CHANGED")

        self.assertEqual(self.file_access.write_file_contents, testfile)
        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))

    def test_that_GIVEN_two_macros_with_only_in_the_globals_file_THEN_only_the_macro_in_the_globals_file_is_changed(self):
        ioc_to_change = "GALOL"

        macros_to_change = [(Macro("DONTCHANGE"), Macro("CHANGED0")),
                            (Macro("CHANGEME"), Macro("CHANGED1"))]

        self.macro_changer.change_macros(ioc_to_change, macros_to_change)

        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))
        self.assertTrue('CHANGED1' in self.file_access.write_file_contents)
        self.assertFalse('CHANGED0' in self.file_access.write_file_contents)

    def test_GIVEN_macro_to_change_with_name_and_value_THEN_the_only_the_macro_matching_both_the_name_and_value_are_changed(self):
        ioc_to_change = "GALOL"
        macros_to_change = [
            (Macro("CHANGEME", "01"), Macro("CHANGED", "001"))
        ]

        self.macro_changer.change_macros(ioc_to_change, macros_to_change)

        # This only changes "GALOL_01__CHANGEME=01" to "GALOL_01__CHANGED=001" and doesn't change any other macros.
        testfile = EXAMPLE_GLOBALS_FILE.replace("CHANGEME=01", "CHANGED=001")

        self.assertEqual(self.file_access.write_file_contents, testfile)
        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))

    def test_that_GIVEN_macro_value_to_change_THEN_the_only_the_macro_value_is_changed(self):
        ioc_to_change = "GALOL"
        macros_to_change = [
            (Macro("CHANGEME", "01"), Macro("CHANGEME", "001"))
        ]

        self.macro_changer.change_macros(ioc_to_change, macros_to_change)

        # This only changes "GALOL_01__CHANGEME=01" to "GALOL_01__CHANGED=001" and doesn't change any other macros.
        testfile = EXAMPLE_GLOBALS_FILE.replace("=01", "=001")

        self.assertEqual(self.file_access.write_file_contents, testfile)
        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))


class TestFilteringIOCs(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.file_access.existing_files = {GLOBALS_FILENAME: GLOBALS_FILENAME}
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacroInGlobals(self.file_access, self.logger)

    def test_GIVEN_globals_file_with_numbered_iocs_requested_WHEN_filtering_THEN_expected_iocs_returned(self):
        root_ioc_name = "GALOL"
        ioc_to_change = root_ioc_name + "_03"

        matching_indices = []
        matched_lines = []
        for index in self.macro_changer._globals_filter_generator(ioc_to_change):
            matching_indices.append(index)
            matched_lines.append(self.macro_changer._loaded_file[index])

        self.assertTrue(all(ioc_to_change in x for x in matched_lines))
        self.assertNotEqual(len(matching_indices), 0)

    def test_GIVEN_globals_file_with_ioc_containing_requested_WHEN_filtering_THEN_nothing_returned(self):
        root_ioc_name = "GALOL"
        ioc_name = "PRE-{}-POST".format(root_ioc_name)

        matching_indices = []
        matched_lines = []
        for index in self.macro_changer._globals_filter_generator(ioc_name):
            matching_indices.append(index)
            matched_lines.append(self.macro_changer._loaded_file[index])

        self.assertEqual(len(matching_indices), 0)


if __name__ == '__main__':
    unittest.main()
