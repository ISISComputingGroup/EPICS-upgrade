import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.upgrade_step_from_3p2p1 import UpgradeStepFrom3p2p1
from test import mother
from .mother import LoggingStub, FileAccessStub


class TestUpgradeStepFrom3p2p1(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom3p2p1()
        self.logger = LoggingStub()

    def test_GIVEN_no_ioc_xml_file_WHEN_upgrade_THEN_error(self):
        self.file_access.open_file = Mock(side_effect=IOError("No configs Exist"))

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")
        assert_that(self.logger.log_err, has_item("Can not find file to modify in config."))

    def test_GIVEN_ioc_xml_file_WHEN_standard_THEN_file_changed(self):

        self.file_access.open_file = Mock(return_value=mother.CLEAN_COMPONENT_BASE_IOC_FILE_v1)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(0), "result")
        assert_that(self.file_access.write_file_contents, is_(mother.CLEAN_COMPONENT_BASE_IOC_FILE_v2))

    def test_GIVEN_ioc_xml_file_has_alarm_ioc_in_already_WHEN_upgrade_THEN_error(self):

        self.file_access.open_file = Mock(return_value=mother.CLEAN_COMPONENT_BASE_IOC_FILE_v2)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

    def test_GIVEN_ioc_xml_file_with_no_ISISDAE_01_ioc_in_WHEN_upgrade_THEN_error(self):

        self.file_access.open_file = Mock(return_value=mother.ERROR_COMPONENT_BASE_IOC_FILE_NO_ISISDAE)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

    def test_GIVEN_ioc_xml_file_with_too_many_ALARMS_in_WHEN_upgrade_THEN_error(self):

        self.file_access.open_file = Mock(return_value=mother.ERROR_COMPONENT_BASE_IOC_FILE_TWO_ALARMS)

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

    def test_GIVEN_ioc_xml_file_which_is_not_xml_WHEN_upgrade_THEN_error(self):

        self.file_access.open_file = Mock(return_value=[""])

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")

if __name__ == '__main__':
    unittest.main()
