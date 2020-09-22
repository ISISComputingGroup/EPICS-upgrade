import os
import unittest
from mock import MagicMock as Mock
from test.test_utils import test_changing_blocks, test_changing_synoptics
from mother import LoggingStub, FileAccessStub
from src.upgrade_step_from_7p2p0 import IgnoreRcpttSynoptics, UpgradeMotionSetPoints
from functools import partial


class TestIgnoreRcpttSynoptics(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = IgnoreRcpttSynoptics()
        self.logger = LoggingStub()

    def test_GIVEN_existing_file_with_no_existing_rpctt_WHEN_writing_content_THEN_append_content(self):
        self.file_access.exists = Mock(return_value=True)
        self.file_access.write_file = Mock()
        self.file_access.line_exists = Mock(return_value=False)
        self.upgrade_step.perform(self.file_access, self.logger)
        self.file_access.write_file.assert_called_once_with(self.upgrade_step.file_name, ["rcptt_*"], "a")

    def test_GIVEN_no_file_WHEN_writing_content_THEN_write_to_new_file(self):
        self.file_access.exists = Mock(return_value=False)
        self.file_access.write_file = Mock()
        # self.file_access.line_exists = Mock(return_value=False)
        self.upgrade_step.perform(self.file_access, self.logger)
        self.file_access.write_file.assert_called_once_with(self.upgrade_step.file_name,
                                                            self.upgrade_step.text_content, "w")

    def test_GVEN_existing_file_with_rpctt_WHEN_writing_content_THEN_do_nothing(self):
        self.file_access.exists = Mock(return_value=True)
        self.file_access.write_file = Mock()
        self.file_access.line_exists = Mock(return_value=True)
        self.upgrade_step.perform(self.file_access, self.logger)
        self.file_access.write_file.assert_not_called()


class TestUpgradeMotionSetPoints(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeMotionSetPoints()
        self.logger = LoggingStub()

    def test_GIVEN_coord_1_WHEN_step_performed_THEN_convert_to_coord_0(self):
        starting_blocks = [("BLOCK_NAME", "COORD1:SOMETHING"), ("BLOCK_NAME_2", "COORD1")]
        expected_blocks = [("BLOCK_NAME", "COORD0:SOMETHING"), ("BLOCK_NAME_2", "COORD0")]

        def action():
            self.upgrade_step.perform(self.file_access, self.logger)

        test_changing_blocks(self.file_access, action, starting_blocks, expected_blocks)
        test_changing_synoptics(self.file_access, action, starting_blocks, expected_blocks)

    def test_GIVEN_coord_2_WHEN_step_performed_THEN_convert_to_coord_1(self):
        starting_blocks = [("BLOCK_NAME", "COORD2:SOMETHING"), ("BLOCK_NAME_2", "COORD2")]
        expected_blocks = [("BLOCK_NAME", "COORD1:SOMETHING"), ("BLOCK_NAME_2", "COORD1")]

        def action():
            self.upgrade_step.perform(self.file_access, self.logger)

        test_changing_blocks(self.file_access, action, starting_blocks, expected_blocks)
        test_changing_synoptics(self.file_access, action, starting_blocks, expected_blocks)

    def test_GIVEN_coord_2_renamed_PVs_WHEN_step_performed_THEN_convert_to_coord_1(self):
        starting_blocks = [("BLOCK_NAME", "COORD2:NO_OFFSET"), ("BLOCK_NAME_2", "COORD2:RBV:OFFSET"),
                           ("BLOCK_NAME_3", "COORD2:LOOKUP:SET:RBV")]
        expected_blocks = [("BLOCK_NAME", "COORD1:NO_OFF"), ("BLOCK_NAME_2", "COORD1:RBV:OFF"),
                           ("BLOCK_NAME_3", "COORD1:SET:RBV")]

        def action():
            self.upgrade_step.perform(self.file_access, self.logger)

        test_changing_blocks(self.file_access, action, starting_blocks, expected_blocks)
        test_changing_synoptics(self.file_access, action, starting_blocks, expected_blocks)

    def test_GIVEN_coord_1_renamed_PVs_WHEN_step_performed_THEN_convert_to_coord_0(self):
        starting_blocks = [("BLOCK_NAME", "COORD1:NO_OFFSET"), ("BLOCK_NAME_2", "COORD1:RBV:OFFSET"),
                           ("BLOCK_NAME_3", "COORD1:LOOKUP:SET:RBV")]
        expected_blocks = [("BLOCK_NAME", "COORD0:NO_OFF"), ("BLOCK_NAME_2", "COORD0:RBV:OFF"),
                           ("BLOCK_NAME_3", "COORD0:SET:RBV")]

        def action():
            self.upgrade_step.perform(self.file_access, self.logger)

        test_changing_blocks(self.file_access, action, starting_blocks, expected_blocks)
        test_changing_synoptics(self.file_access, action, starting_blocks, expected_blocks)


if __name__ == '__main__':
    unittest.main()
