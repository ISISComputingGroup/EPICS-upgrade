import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.upgrade_step_from_4p0p0 import UpgradeStepFrom4p0p0
from test import mother
from mother import LoggingStub, FileAccessStub


class TestUpgradeStepFrom4p0p0(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom4p0p0()
        self.logger = LoggingStub()

    def test_GIVEN_no_synoptic_xml_files_WHEN_upgrade_THEN_silent_pass(self):
        self.file_access.iterate_directory = Mock(return_value=[])

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")

    def test_GIVEN_cant_open_xml_file_WHEN_upgrade_THEN_error(self):
        self.file_access.iterate_directory = Mock(return_value=["somefile.xml"])
        self.file_access.open_xml_file = Mock(side_effect=IOError("Cannot open file"))

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")
        assert_that(self.logger.log_err, has_item("Can not open file to modify in config."))

    def test_GIVEN_synoptic_xml_file_WHEN_standard_THEN_file_changed(self):
        self.file_access.iterate_directory = Mock(return_value=["somefile.xml"])
        self.file_access.open_file = Mock(return_value=mother.RENAME_SYNOPTIC_PRE4P0P0)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")
        assert_that(self.file_access.write_file_contents.replace('\n', ''),
                    equal_to_ignoring_whitespace(mother.RENAME_SYNOPTIC_POST4P0P0.replace('\n', '')))

    def test_GIVEN_multiple_synoptic_xml_files_WHEN_standard_THEN_files_changed(self):
        self.file_access.iterate_directory = Mock(return_value=["somefile.xml", "otherfile.xml"])
        self.file_access.open_file = Mock(return_value=mother.RENAME_SYNOPTIC_PRE4P0P0)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")
        assert_that(self.file_access.write_file_contents.replace('\n', ''),
                    equal_to_ignoring_whitespace(mother.RENAME_SYNOPTIC_POST4P0P0.replace('\n', '')))

    def test_GIVEN_synoptic_xml_file_which_is_not_xml_WHEN_upgrade_THEN_error(self):
        self.file_access.iterate_directory = Mock(return_value=["somefile.xml"])
        self.file_access.open_file = Mock(return_value="<")

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

if __name__ == '__main__':
    unittest.main()
