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
        self.file_access.listdir = Mock(side_effect=WindowsError("No synoptics directory exists"))

        result = self.upgrade_step.perform(self.file_access, self.logger)

        assert_that(result, is_(not_(0)), "result")
        assert_that(self.logger.log_err, has_item("Unable to find the synoptics directory"))

if __name__ == '__main__':
    unittest.main()
