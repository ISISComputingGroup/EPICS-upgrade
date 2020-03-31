import unittest
from hamcrest import *
from src.common_upgrades.change_pvs_in_xml import ChangePVsInXML
from test.mother import LoggingStub, FileAccessStub
from mock import MagicMock as Mock


BLOCK_NAMESPACE = "http://epics.isis.rl.ac.uk/schema/blocks/1.0"


BLOCK_FILE_XML = """<?xml version="1.0" ?><blocks xmlns="{namespace}" xmlns:blk="{namespace}" xmlns:xi="http://www.w3.org/2001/XInclude">
    {{blocks}}
</blocks>""".format(namespace=BLOCK_NAMESPACE)


BLOCK_XML = """
<block>
    <name>{name}</name>
    <read_pv>{pv}</read_pv>
</block>
"""


SYNOPTIC_NAMESPACE = "http://www.isis.stfc.ac.uk//instrument"


SYNOPTIC_FILE_XML = """<?xml version="1.0" ?><instrument xmlns="{namespace}">
    <name>TEST</name>
    <components>
        <component>
            <name>COMPONENT_NAME</name>
            <type>UNKNOWN</type>
            <target/>
            <pvs>
                {{blocks}}
            </pvs>
        </component>
    </components>
</instrument>""".format(namespace=SYNOPTIC_NAMESPACE)


SYNOPTIC_XML = """
<pv>
    <displayname>{name}</displayname>
    <address>{pv}</address>
    <recordtype>
        <io>READ</io>
    </recordtype>
</pv>
"""


def create_pv_xml(file_xml, pv_xml, pv_dict):
    block_xml = "".join([pv_xml.format(name=pv[0], pv=pv[1]) for pv in pv_dict])
    return file_xml.format(blocks=block_xml)


class TestChangePVs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.pv_changer = ChangePVsInXML(self.file_access, self.logger)

    def _test_changing_pv(self, starting_blocks, pv_to_change, new_pv, expected_blocks):
        self._test_changing_blocks(starting_blocks, pv_to_change, new_pv, expected_blocks)
        self._test_changing_synoptics(starting_blocks, pv_to_change, new_pv, expected_blocks)

    def _test_changing_blocks(self, starting_blocks, pv_to_change, new_pv, expected_blocks):
        # Given:
        self.file_access.open_file = Mock(return_value=create_pv_xml(BLOCK_FILE_XML, BLOCK_XML, starting_blocks))
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(return_value=[("file1.xml", self.file_access.open_xml_file(None))])

        # When:
        self.pv_changer.change_pv_name_in_blocks(pv_to_change, new_pv)

        # Then:
        expected_xml = create_pv_xml(BLOCK_FILE_XML, BLOCK_XML, expected_blocks)
        assert_that(self.file_access.write_file_contents, is_(expected_xml))

    def _test_changing_synoptics(self, starting_blocks, pv_to_change, new_pv, expected_blocks):
        # Given:
        self.file_access.open_file = Mock(return_value=create_pv_xml(SYNOPTIC_FILE_XML, SYNOPTIC_XML, starting_blocks))
        self.file_access.write_file = Mock()
        self.file_access.get_synoptic_files = Mock(return_value=[("file1.xml", self.file_access.open_xml_file(None))])

        # When:
        self.pv_changer.change_pv_names_in_synoptics(pv_to_change, new_pv)

        # Then:
        expected_xml = create_pv_xml(SYNOPTIC_FILE_XML, SYNOPTIC_XML, expected_blocks)
        assert_that(self.file_access.write_file_contents, is_(expected_xml))

    def test_GIVEN_multiple_different_blocks_in_configuration_WHEN_ones_pv_is_changed_THEN_only_that_block_changes(self):
        self._test_changing_pv([("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGEME")], "CHANGEME", "CHANGED",
                               [("BLOCKNAME", "BLOCK_PV"), ("BLOCKNAME_2", "CHANGED")])

    def test_GIVEN_block_with_part_of_PV_WHEN_pv_is_changed_THEN_only_part_of_PV_changes(self):
        self._test_changing_pv([("BLOCKNAME", "CHANGEME:BUT:NOT:ME")], "CHANGEME", "CHANGED",
                               [("BLOCKNAME", "CHANGED:BUT:NOT:ME")])

    def test_GIVEN_two_blocks_that_need_changing_WHEN_pv_is_changed_THEN_both_change(self):
        self._test_changing_pv([("BLOCKNAME", "CHANGEME:BUT:NOT:ME"), ("BLOCKNAME_1", "ALSO:CHANGEME:BUT:NOT:ME")],
                               "CHANGEME", "CHANGED",
                               [("BLOCKNAME", "CHANGED:BUT:NOT:ME"), ("BLOCKNAME_1", "ALSO:CHANGED:BUT:NOT:ME")])

    def test_GIVEN_block_with_name_that_could_be_changed_WHEN_pv_is_changed_THEN_name_is_not(self):
        self._test_changing_pv([("CHANGEME", "BLAH")], "CHANGEME", "CHANGED",
                               [("CHANGEME", "BLAH")])


if __name__ == '__main__':
    unittest.main()
