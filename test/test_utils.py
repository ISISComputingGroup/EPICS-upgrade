import six
from hamcrest import *
from src.common_upgrades.utils.constants import BLOCK_FILE

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


def create_xml_with_starting_blocks(file_access, starting_blocks):
    def open_file(filename):
        if filename == file_access.SYNOPTIC_FILENAME:
            return create_pv_xml(SYNOPTIC_FILE_XML, SYNOPTIC_XML, starting_blocks)
        elif filename == BLOCK_FILE:
            return create_pv_xml(BLOCK_FILE_XML, BLOCK_XML, starting_blocks)
    file_access.open_file = open_file


def _set_starting_blocks_and_perform_action(file_access, action, starting_blocks):
    create_xml_with_starting_blocks(file_access, starting_blocks)
    action()


def test_changing_synoptics_and_blocks(file_access, action, starting_blocks, expected_blocks):
    _set_starting_blocks_and_perform_action(file_access, action, starting_blocks)

    expected_xml = create_pv_xml(SYNOPTIC_FILE_XML, SYNOPTIC_XML, expected_blocks)
    assert_that(file_access.write_file_dict[file_access.SYNOPTIC_FILENAME], is_(expected_xml))

    expected_xml = create_pv_xml(BLOCK_FILE_XML, BLOCK_XML, expected_blocks)
    assert_that(file_access.write_file_dict[BLOCK_FILE], is_(expected_xml))


def test_action_does_not_write(file_access, action, starting_blocks):
    _set_starting_blocks_and_perform_action(file_access, action, starting_blocks)

    assert_that(file_access.SYNOPTIC_FILENAME, not_(is_in(six.iterkeys(file_access.write_file_dict))))
    assert_that(BLOCK_FILE, not_(is_in(six.iterkeys(file_access.write_file_dict))))