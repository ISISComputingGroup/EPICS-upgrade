import os
import unittest
from mock import MagicMock as Mock
from mock import ANY
from mother import LoggingStub, FileAccessStub
from src.upgrade_step_from_7p2p0 import IgnoreRcpttSynoptics


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


if __name__ == '__main__':
    unittest.main()
