import unittest
from hamcrest import *
from functools import partial
from src.common_upgrades.change_macro_in_globals import ChangeMacroInGlobals
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs, EXAMPLE_GLOBALS_FILE
import os


def generate_many_iocs(configs):
    for config, iocs in configs.items():
        yield (config, create_xml_with_iocs(iocs))


class TestChangeMacroInGlobals(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacroInGlobals(self.file_access, self.logger)

    def test_WHEN_asked_to_load_globals_file_THEN_the_default_globals_file_is_loaded(self):
        result = self.macro_changer.load_globals_file()

        reference = EXAMPLE_GLOBALS_FILE.split("\n")

        assert_that(result, reference)

    def test_GIVEN_globals_file_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        ioc_to_change = "CHANGE_ME"

        matching_indices = []
        for index in self.macro_changer._globals_filter_generator(ioc_to_change):
            matching_indices.append(index)

        self.assertEqual(len(matching_indices), 0)

    def test_GIVEN_globals_file_with_requested_iocs_WHEN_filtering_THEN_expected_ioc_returned(self):
        ioc_to_change = "BINS"

        matching_indices = []
        matched_lines = []
        for index in self.macro_changer._globals_filter_generator(ioc_to_change):
            matching_indices.append(index)
            matched_lines.append(self.macro_changer._loaded_file[index])

        self.assertEqual(len(matching_indices), 1)
        self.assertIn("BINS", matched_lines[0])

    def test_GIVEN_globals_file_with_requested_ioc_WHEN_after_filtering_THEN_ioc_saved_to_file(self):
        ioc_to_change = "GALOL"
        macro_to_apply = {"ioc_name": ioc_to_change,
                          "current_state": "CHANGEME",
                          "new_state": "CHANGED"}

        self.macro_changer.apply_macro_change(macro_to_apply)

        testfile = EXAMPLE_GLOBALS_FILE.replace(macro_to_apply["current_state"],
                                                macro_to_apply["new_state"])

        self.assertEqual(self.file_access.write_file_contents, testfile)
        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))

    def test_GIVEN_globals_file_with_requested_ioc_WHEN_changed_after_filtering_THEN_changed_file_written(self):
        ioc_to_change = "GALOL"

        macros_to_apply = [{"ioc_name": ioc_to_change, "current_state": "DONTCHANGE", "new_state": "CHANGED0"},
                           {"ioc_name": ioc_to_change, "current_state": "CHANGEME", "new_state": "CHANGED1"}]

        for macro in macros_to_apply:
            self.macro_changer.apply_macro_change(macro)

        self.assertEqual(self.file_access.write_filename, os.path.join("configurations", "globals.txt"))
        self.assertTrue('CHANGED1' in self.file_access.write_file_contents)
        self.assertFalse('CHANGED0' in self.file_access.write_file_contents)

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
