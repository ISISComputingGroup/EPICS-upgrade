from mock import Mock
from hamcrest import *


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


def create_xml_with_starting_blocks(file_access, starting_blocks, is_config=True):
    if is_config:
        file_xml, individual_xml = BLOCK_FILE_XML, BLOCK_XML
    else:
        file_xml, individual_xml = SYNOPTIC_FILE_XML, SYNOPTIC_XML
    file_access.open_file = Mock(return_value=create_pv_xml(file_xml, individual_xml, starting_blocks))
    file_access.write_file = Mock()
    file_returned = [("file1.xml", file_access.open_xml_file(None))]
    if is_config:
        file_access.get_config_files = Mock(return_value=file_returned)
    else:
        file_access.get_synoptic_files = Mock(return_value=file_returned)


def test_changing_blocks(file_access, action, starting_blocks, expected_blocks):
    # Given:
    create_xml_with_starting_blocks(file_access, starting_blocks)

    # When:
    action()
    # Then:
    expected_xml = create_pv_xml(BLOCK_FILE_XML, BLOCK_XML, expected_blocks)
    assert_that(file_access.write_file_contents, is_(expected_xml))


def test_changing_synoptics(file_access, action, starting_blocks, expected_blocks):
    # Given:
    create_xml_with_starting_blocks(file_access, starting_blocks, False)

    # When:
    action()

    # Then:
    expected_xml = create_pv_xml(SYNOPTIC_FILE_XML, SYNOPTIC_XML, expected_blocks)
    assert_that(file_access.write_file_contents, is_(expected_xml))