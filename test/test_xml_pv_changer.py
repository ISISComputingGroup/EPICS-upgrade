import unittest

from hamcrest import *

from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML
from test.mother import FileAccessStub, LoggingStub
from test.test_utils import (
    create_xml_with_starting_blocks,
    test_changing_synoptics_and_blocks,
)


class TestChangePVs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()

    def _test_changing_pv(self, starting_blocks, pv_to_change, new_pv, expected_blocks):
        def action():
            pv_changer = ChangePVsInXML(self.file_access, self.logger)
            pv_changer.change_pv_name(pv_to_change, new_pv)

        test_changing_synoptics_and_blocks(
            self.file_access, action, starting_blocks, expected_blocks
        )

    def test_GIVEN_multiple_different_blocks_in_configuration_WHEN_ones_pv_is_changed_THEN_only_that_block_changes(
        self,
    ):
        self._test_changing_pv(
            [("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGEME")],
            "CHANGEME",
            "CHANGED",
            [("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGED")],
        )

    def test_GIVEN_block_with_part_of_PV_WHEN_pv_is_changed_THEN_only_part_of_PV_changes(
        self,
    ):
        self._test_changing_pv(
            [("BLOCKNAME", "CHANGEME:BUT:NOT:ME")],
            "CHANGEME",
            "CHANGED",
            [("BLOCKNAME", "CHANGED:BUT:NOT:ME")],
        )

    def test_GIVEN_two_blocks_that_need_changing_WHEN_pv_is_changed_THEN_both_change(
        self,
    ):
        self._test_changing_pv(
            [
                ("BLOCKNAME", "CHANGEME:BUT:NOT:ME"),
                ("BLOCKNAME_1", "ALSO:CHANGEME:BUT:NOT:ME"),
            ],
            "CHANGEME",
            "CHANGED",
            [
                ("BLOCKNAME", "CHANGED:BUT:NOT:ME"),
                ("BLOCKNAME_1", "ALSO:CHANGED:BUT:NOT:ME"),
            ],
        )

    def test_GIVEN_block_with_name_that_could_be_changed_WHEN_pv_is_changed_THEN_name_is_not(
        self,
    ):
        self._test_changing_pv(
            [("CHANGEME", "BLAH")], "CHANGEME", "CHANGED", [("CHANGEME", "BLAH")]
        )

    def GIVEN_two_blocks_with_pvs_that_obey_filter_WHEN_pv_counted_THEN_returns_two_and_xml_unchanged(
        self,
    ):
        starting_blocks = [
            ("BLOCKNAME", "CHANGEME:BUT:NOT:ME"),
            ("BLOCKNAME_1", "ALSO:CHANGEME:BUT:NOT:ME"),
        ]
        create_xml_with_starting_blocks(self.file_access, starting_blocks)

        pv_changer = ChangePVsInXML(self.file_access, self.logger)
        number_of_pvs = pv_changer.get_number_of_instances_of_pv("CHANGEME")

        assert_that(number_of_pvs, is_(2))
        self.file_access.write_file.assert_not_called()

    def GIVEN_block_with_name_that_obeys_filter_WHEN_pv_counted_THEN_returns_zero_and_xml_unchanged(
        self,
    ):
        starting_blocks = [("CHANGEME", "BLAH")]
        create_xml_with_starting_blocks(self.file_access, starting_blocks)

        pv_changer = ChangePVsInXML(self.file_access, self.logger)
        number_of_pvs = pv_changer.get_number_of_instances_of_pv("CHANGEME")

        assert_that(number_of_pvs, is_(0))
        self.file_access.write_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
