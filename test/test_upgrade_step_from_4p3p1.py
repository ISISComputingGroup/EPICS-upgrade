import unittest
from hamcrest import *
from mock import MagicMock as Mock
import xml.etree.ElementTree as ET
from src.upgrade_step_from_4p3p1 import UpgradeStepFrom4p3p1
from mother import LoggingStub, FileAccessStub, create_xml_with_iocs

NAMESPACE = "http://epics.isis.rl.ac.uk/schema/iocs/1.0"

IOC_FILE_XML = """<?xml version="1.0" ?><iocs xmlns="{namespace}" xmlns:ioc="{namespace}" xmlns:xi="http://www.w3.org/2001/XInclude">
    {{iocs}}
</iocs>""".format(namespace=NAMESPACE)

IOC_XML = """
<ioc name="{name}">
    <macros>
        {macros}
    </macros>
    <pvs/>
    <pvsets/>
</ioc>
"""

MACRO_XML = """
<macro name="{name}" value="{value}"/>
"""


def create_ioc(ioc_name, ioc_num, macros):
    macro_xml = "".join([MACRO_XML.format(name=name, value=value) for name, value in macros.items()])
    return IOC_XML.format(name="{}_{:0>2}".format(ioc_name, ioc_num), macros=macro_xml)


class TestUpgradeStepFrom4p3p1(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom4p3p1()
        self.logger = LoggingStub()

    def _test_GIVEN_input_macros_when_macros_changed_THEN_new_macros_in_new_format(self, original_macros):

        # Arrange
        original_macros_with_values = dict()
        for macro in original_macros:
            original_macros_with_values[macro] = ""
        xml = IOC_FILE_XML.format(iocs=create_ioc("PIMOT", 1, original_macros_with_values))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        # Act
        self.upgrade_step.change_pimot_macros(self.file_access, self.logger)

        # Assert
        assert_that(self.file_access.write_file_contents, is_not(None))
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        macro_names = [m.attrib["name"] for m in written_xml.findall(".//ns:macro", {"ns": NAMESPACE})]

        assert_that(len(macro_names), is_(2))
        assert_that(set(macro_names) == set(("PORT", "BAUD")))

    def test_GIVEN_new_macro_format_WHEN_macros_changed_THEN_macros_unaffected(self):
        self._test_GIVEN_input_macros_when_macros_changed_THEN_new_macros_in_new_format(("PORT", "BAUD"))

    def test_GIVEN_both_macros_in_old_format_WHEN_macros_changed_THEN_both_macros_updated(self):
        self._test_GIVEN_input_macros_when_macros_changed_THEN_new_macros_in_new_format(("PORT1", "BAUD1"))

    def test_GIVEN_port_macro_in_old_format_WHEN_macros_changed_THEN_port_macro_updated(self):
        self._test_GIVEN_input_macros_when_macros_changed_THEN_new_macros_in_new_format(("PORT1", "BAUD"))

    def test_GIVEN_baud_macro_in_old_format_WHEN_macros_changed_THEN_baud_macro_updated(self):
        self._test_GIVEN_input_macros_when_macros_changed_THEN_new_macros_in_new_format(("PORT", "BAUD1"))

    def test_GIVEN_old_macro_format_on_not_PIMOT_ioc_WHEN_macros_changed_THEN_file_not_touched(self):
        xml = IOC_FILE_XML.format(iocs=create_ioc("NOT_A_PIMOT", 1, {"PORT1": "", "BAUD1": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        self.upgrade_step.change_pimot_macros(self.file_access, self.logger)

        assert_that(self.file_access.write_file_contents, is_(None))


if __name__ == '__main__':
    unittest.main()
