import unittest
import mock

from mother import FileAccessStub, LoggingStub
from src.upgrade_step_from_12p0p0 import UpgradeJawsForPositionAutosave


class TestUpgradeJawsForPositionAutosave(unittest.TestCase):

    def setUp(self):
        self.logger = LoggingStub()
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeJawsForPositionAutosave()
    
    
    def _perform(self, substitution_files: tuple[str], batch_files: tuple[str], matches: list[bool], batch_files_contents: list[list[str]]):
        self.file_access.get_file_paths = mock.Mock(side_effect=[substitution_files, batch_files])
        self.file_access.file_contains = mock.Mock(side_effect=matches)
        self.file_access.open_file = mock.Mock(side_effect=batch_files_contents)
        self.file_access.write_file = mock.Mock()
        return self.upgrade_step.perform(self.file_access, self.logger)

    def test_GIVEN_files_with_correct_db_and_no_macros_WHEN_upgrade_THEN_macros_added_correctly(self):
        substitution_files = ("jaws.substitutions", "name.substitutions")
        batch_files = ("jaws.cmd", "other.cmd")
        matches = [True, True]
        batch_files_contents= [
            ["""# Comment""",                                                           # Unrelated text.
             """dbLoadRecords("\\jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:,")""",      # Trailing comma.
             """dbLoadRecords("jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:")"""],        # Local db file path.

            ["""dbLoadRecordsList("\\name.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:")""",  # Alternate load function.
             """dbLoadRecords("/not_name.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:")""",    # Partial match.
             """"""]]                                                                   # White space.

        self.assertEqual(self._perform(substitution_files, batch_files, matches, batch_files_contents), 0)
        
        self.file_access.write_file.assert_has_calls([
            mock.call(
                "jaws.cmd",
                ["""# Comment""",
                 """dbLoadRecords("\\jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:,IFINIT_FROM_AS=$(IFINIT_JAWS_FROM_AS=#),IFNOTINIT_FROM_AS=$(IFNOTINIT_JAWS_FROM_AS=)")""",
                 """dbLoadRecords("jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:,IFINIT_FROM_AS=$(IFINIT_JAWS_FROM_AS=#),IFNOTINIT_FROM_AS=$(IFNOTINIT_JAWS_FROM_AS=)")"""]
            ),
            mock.call(
                "other.cmd",
                ["""dbLoadRecordsList("\\name.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:,IFINIT_FROM_AS=$(IFINIT_JAWS_FROM_AS=#),IFNOTINIT_FROM_AS=$(IFNOTINIT_JAWS_FROM_AS=)")""",
                 """dbLoadRecords("/not_name.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:")""",
                 """"""]
            )])

    def test_GIVEN_file_with_correct_db_and_macros_WHEN_upgrade_THEN_no_writes(self):
        substitution_files = ("jaws.substitutions",)
        batch_files = ("jaws.cmd",)
        matches = [True]
        batch_files_contents= [
            ["""dbLoadRecords("/jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:,IFINIT_FROM_AS=$(IFINIT_JAWS_FROM_AS=#),IFNOTINIT_FROM_AS=$(IFNOTINIT_JAWS_FROM_AS=)"")"""]
        ]

        self.assertEqual(self._perform(substitution_files, batch_files, matches, batch_files_contents), 0)
        
        self.file_access.write_file.assert_not_called()

    def test_GIVEN_file_without_db_WHEN_upgrade_THEN_no_writes(self):
        substitution_files = ("jaws.substitutions",)
        batch_files = ("jaws.cmd",)
        matches = [False]
        batch_files_contents= [
            ["""dbLoadRecords("/other.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:"")"""]
        ]

        self.assertEqual(self._perform(substitution_files, batch_files, matches, batch_files_contents), 0)
        
        self.file_access.write_file.assert_not_called()

    def test_GIVEN_file_with_a_match_but_no_changes_WHEN_upgrade_THEN_no_write_and_step_failed(self):
        substitution_files = ("jaws.substitutions",)
        batch_files = ("jaws.cmd",)
        matches = [True]
        batch_files_contents= [
            ["""dbLoadRecords("/jaws.db","P=$(MYPVPREFIX)MOT:,MACRO=MACRO:"") # Load with a comment after."""]
        ]

        self.assertNotEqual(self._perform(substitution_files, batch_files, matches, batch_files_contents), 0)
        
        self.file_access.write_file.assert_not_called()
