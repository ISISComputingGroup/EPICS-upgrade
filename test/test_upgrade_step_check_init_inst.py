import unittest
from hamcrest import assert_that, equal_to, is_not
from mock import MagicMock, patch, mock_open
from mother import LoggingStub, FileAccessStub
from src.upgrade_step_check_init_inst import UpgradeStepCheckInitInst
import os

import sys
module_ = "builtins"
module_ = module_ if module_ in sys.modules else 'builtins'

try:
    import unittest.mock as mock
except (ImportError,) as e:
    import mock 

class TestUpgradeStepCheckInitInst(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepCheckInitInst()
        self.logger = LoggingStub()
        self.directory_structure = [
            ("root", ["dir1", "dir2"], ["init_file1"]),
            ("root\\dir1", ["dir3"], ["init_file2", "init_file3"]),
            ("root\\dir2", [], ["init_file4"]),
            ("root\\dir3", [], []),
        ]

    def test_GIVEN_no_file_called_init_inst_WHEN_search_files_THEN_zero_returned(self):
        # Arrange
        file_names = ["init", "my_init", "another_file"]
        root = "myfolder"
        # Act and Assert
        assert_that(self.upgrade_step.search_files(file_names, root, self.file_access),
            equal_to(0), "File starting with init_inst is not in filenames, so no pre or post cmd would be found by genie")
        
    @patch('builtins.open', mock_open(read_data=""), create=True)
    def test_GIVEN_file_with_name_none_containing_pre_post_cmd_WHEN_search_files_THEN_zero_returned(self):
        # Arrange
        file_names = ["init", "init_larmor", "another_file"]
        root = "myfolder"
        # Act and Assert
        assert_that(self.upgrade_step.search_files(file_names, root, self.file_access),
            equal_to(0), "pre or post cmd not in init_larmor file, therefore this is ok")

    @patch('builtins.open', mock_open(read_data="precmd"), create=True)
    def test_GIVEN_file_with_name_containing_precmd_WHEN_search_files_THEN_error_returned(self):
        # Arrange
        file_names = ["init", "init_zoom", "another_file"]
        root = "myfolder"
        # Act and Assert
        assert_that(self.upgrade_step.search_files(file_names, root, self.file_access),
            is_not(equal_to(0)), "pre cmd in init_zoom file, therefore error message should be returned")

    @patch('builtins.open', mock_open(read_data="postcmd"))
    def test_GIVEN_file_with_name_containing_postcmd_WHEN_search_files_THEN_error_returned(self):
        # Arrange
        file_names = ["init", "init_inst", "another_file"]
        root = "myfolder"
        # Act and Assert
        assert_that(self.upgrade_step.search_files(file_names, root, self.file_access),
            is_not(equal_to(0)), "postcmd in init_inst file, therefore error message should be returned")

    @patch('builtins.open', mock_open(read_data="postcmd precmd"))
    def test_GIVEN_file_with_name_containing_pre_and_post_cmd_WHEN_search_files_THEN_error_returned(self):
        # Arrange
        file_names = ["init", "init_iris", "another_file"]
        root = "myfolder"
        # Act and Assert
        assert_that(self.upgrade_step.search_files(file_names, root, self.file_access),
            is_not(equal_to(0)), "pre and post cmd in init_iris file, therefore error message should be returned")

    def test_GIVEN_directory_structure_and_no_cmd_WHEN_search_folders_THEN_files_and_folders_walked_and_zero_returned(self):
        # Arrange
        file_search_returns = [0, 0, 0, 0] # One return for each of file1, 2, 3 and 4
        with patch('os.walk', return_value=self.directory_structure) as mocked_walk,\
             patch('src.upgrade_step_check_init_inst.UpgradeStepCheckInitInst.search_files', side_effect=file_search_returns) as mocked_search_files:
            # Act
            search_return = self.upgrade_step.search_folder("any", self.file_access)
            # Assert
            assert_that(mocked_search_files.call_count, equal_to(4), "Four files to search, each should be called")
            assert_that(search_return, equal_to(0), "Should pass successfully")
    
    def test_GIVEN_directory_structure_and_file_at_top_level_contains_precmd_WHEN_search_folders_THEN_error_returned(self):
        # Arrange
        file_search_returns = ["Error precmd", 0, 0, 0] # One return for each of file1, 2, 3 and 4
        with patch('os.walk', return_value=self.directory_structure) as mocked_walk,\
             patch('src.upgrade_step_check_init_inst.UpgradeStepCheckInitInst.search_files', side_effect=file_search_returns) as mocked_search_files:
            # Act
            search_return = self.upgrade_step.search_folder("any", self.file_access)
            # Assert
            assert_that(mocked_search_files.call_count, equal_to(4), "Should search all files")
            assert_that(search_return, equal_to(file_search_returns[0]+"\n"), "Return error from searched file")

    def test_GIVEN_directory_structure_and_file_at_second_level_contains_postcmd_WHEN_search_folders_THEN_error_returned(self):
        # Arrange
        file_search_returns = [0, 0, "Error postcmd", 0] # One return for each of file1, 2, 3 and 4
        with patch('os.walk', return_value=self.directory_structure) as mocked_walk,\
             patch('src.upgrade_step_check_init_inst.UpgradeStepCheckInitInst.search_files', side_effect=file_search_returns) as mocked_search_files:
            # Act
            search_return = self.upgrade_step.search_folder("any", self.file_access)
            # Assert
            assert_that(mocked_search_files.call_count, equal_to(4), "Should search all files")
            assert_that(search_return, equal_to(file_search_returns[2]+"\n"), "Return error from searched file")

    def test_GIVEN_directory_structure_and_two_files_contain_cmd_WHEN_search_folders_THEN_error_returned(self):
        # Arrange
        file_search_returns = ["Error precmd", 0, "Error postcmd", 0] # One return for each of file1, 2, 3 and 4
        with patch('os.walk', return_value=self.directory_structure) as mocked_walk,\
             patch('src.upgrade_step_check_init_inst.UpgradeStepCheckInitInst.search_files', side_effect=file_search_returns) as mocked_search_files:
            # Act
            search_return = self.upgrade_step.search_folder("any", self.file_access)
            # Assert
            assert_that(mocked_search_files.call_count, equal_to(4), "Should search all files")
            assert_that(search_return, equal_to(file_search_returns[0]+"\n"+file_search_returns[2]+"\n"), "Return error from searched file")
