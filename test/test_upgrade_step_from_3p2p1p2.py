import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.upgrade_step_from_3p2p1p2 import UpgradeStepFrom3p2p1p2
from test import mother
from mother import LoggingStub, FileAccessStub


class TestUpgradeStepFrom3p2p1p2(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom3p2p1p2()
        self.logger = LoggingStub()

    def test_GIVEN_no_synoptics_xml_file_WHEN_upgrade_THEN_error(self):
        self.file_access.listdir = Mock(side_effect=OSError("No synoptics directory exists"))

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")
        assert_that(self.logger.log_err, has_item("Unable to find the synoptics directory"))

    def test_GIVEN_synoptic_xml_file_has_no_opi_path_WHEN_upgrade_THEN_no_error(self):

        self.file_access.open_file = Mock(return_value=mother.CLEAN_SYNOPTIC_v3p2p1p2)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")

    def test_GIVEN_synoptic_xml_file_has_old_opi_path_WHEN_upgrade_THEN_no_error(self):

        self.file_access.open_file = Mock(return_value=mother.DIRECT_PATH_SYNOPTIC_v3p2p1p2)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")

    def test_GIVEN_synoptic_xml_file_has_new_opi_path_WHEN_upgrade_THEN_no_error(self):

        self.file_access.open_file = Mock(return_value=mother.DIRECT_PATH_SYNOPTIC_v4p0p0)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")

    def test_GIVEN_synoptic_xml_file_has_unknown_opi_path_WHEN_upgrade_THEN_error(self):

        self.file_access.open_file = Mock(return_value=mother.UNKNOWN_SYNOPTIC_v3p2p1p2)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

if __name__ == '__main__':
    unittest.main()
