import unittest
from hamcrest import *
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML
from test.mother import LoggingStub, FileAccessStub
from mock import MagicMock as Mock


NAMESPACE = "http://epics.isis.rl.ac.uk/schema/blocks/1.0"


BLOCK_FILE_XML = """<?xml version="1.0" ?><blocks xmlns="{namespace}" xmlns:blk="{namespace}" xmlns:xi="http://www.w3.org/2001/XInclude">
    {{blocks}}
</blocks>""".format(namespace=NAMESPACE)


BLOCK_XML = """
<block>
    <name>{name}</name>
    <read_pv>{pv}</read_pv>
</block>
"""


def create_block_xml(block_dict):
    block_xml = "".join([BLOCK_XML.format(name=block[0], pv=block[1]) for block in block_dict])
    return BLOCK_FILE_XML.format(blocks=block_xml)


class TestChangePVs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.pv_changer = ChangePVsInXML(self.file_access, self.logger)

    def _test_changing_blocks(self, starting_blocks, pv_to_change, new_pv, expected_blocks):
        # Given:
        self.file_access.open_file = Mock(return_value=create_block_xml(starting_blocks))
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(return_value=[("file1.xml", self.file_access.open_xml_file(None))])

        # When:
        self.pv_changer.change_pv_name(pv_to_change, new_pv)

        # Then:
        expected_block_xml = create_block_xml(expected_blocks)
        assert_that(self.file_access.write_file_contents, is_(expected_block_xml))

    def test_GIVEN_multiple_different_blocks_in_configuration_WHEN_ones_pv_is_changed_THEN_only_that_block_changes(self):
        self._test_changing_blocks([("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGEME")], "CHANGEME", "CHANGED",
                                   [("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGED")])

    def test_GIVEN_block_with_part_of_PV_WHEN_pv_is_changed_THEN_only_part_of_PV_changes(self):
        self._test_changing_blocks([("BLOCKNAME", "CHANGEME:BUT:NOT:ME")], "CHANGEME", "CHANGED",
                                   [("BLOCKNAME", "CHANGED:BUT:NOT:ME")])

    def test_GIVEN_two_blocks_that_need_changing_WHEN_pv_is_changed_THEN_both_change(self):
        self._test_changing_blocks([("BLOCKNAME", "CHANGEME:BUT:NOT:ME"), ("BLOCKNAME_1", "ALSO:CHANGEME:BUT:NOT:ME")],
                                   "CHANGEME", "CHANGED",
                                   [("BLOCKNAME", "CHANGED:BUT:NOT:ME"), ("BLOCKNAME_1", "ALSO:CHANGED:BUT:NOT:ME")])

    def test_GIVEN_block_with_name_that_could_be_changed_WHEN_pv_is_changed_THEN_name_is_not(self):
        self._test_changing_blocks([("CHANGEME", "BLAH")], "CHANGEME", "CHANGED",
                                   [("CHANGEME", "BLAH")])


if __name__ == '__main__':
    unittest.main()
