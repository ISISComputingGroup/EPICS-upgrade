import unittest
from hamcrest import *
from functools import partial
from src.common_upgrades.change_macros_in_xml import ChangeMacrosInXML
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs
from xml.dom import minidom
from mock import MagicMock as Mock
import xml.etree.ElementTree as ET


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


def generate_many_iocs(configs):
    for config, iocs in configs.items():
        yield (config, create_xml_with_iocs(iocs))


def create_galil_ioc(galil_num, macros):
    macro_xml = "".join([MACRO_XML.format(name=name, value=value) for name, value in macros.items()])
    return IOC_XML.format(name="GALIL_{:0>2}".format(galil_num), macros=macro_xml)


class TestTagGenerator(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        # Given:
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change)))

        # Then:
        assert_that(len(list(result)), is_(0), "no results")

    def test_that_GIVEN_two_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        # Given:
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"], "CONFIG_2": ["OTHER_IOC"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change)))

        # Then:
        assert_that(len(list(result)), is_(0), "no results")

    def test_that_GIVEN_xml_with_requested_iocs_WHEN_filtering_THEN_expected_ioc_returned(self):
        # Given:
        ioc_to_change = "CHANGE_ME"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_to_change, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change)))

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_that_GIVEN_one_xml_with_requested_iocs_and_one_without_WHEN_filtering_THEN_only_expected_ioc_returned(self):
        # Given:
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        configs = {good_config: [ioc_to_change, "ANOTHER_ONE"], "CONFIG_2": ["DONT_CHANGE", "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change)))

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_that_GIVEN_xml_with_numbered_ioc_WHEN_filtering_THEN_expected_ioc_returned(self):
        # Given
        root_ioc_name = "CHANGE_ME"
        ioc_name = root_ioc_name + "_03"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, root_ioc_name)))

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_name))

    def test_that_GIVEN_xml_with_ioc_containing_requested_WHEN_filtering_THEN_nothing_returned(self):
        # Given:
        root_ioc_name = "CHANGE_ME"
        ioc_name = "PRE-{}-POST".format(root_ioc_name)
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer.ioc_tag_generator(config, xml, root_ioc_name)))

        # Then:
        assert_that(len(result), is_(0))


class TestChangMacroName(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_old_ioc_macros_THEN_macros_are_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="BAUD1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = "BAUD1"
        new_macro = "BAUD"

        # When:
        self.macro_changer._change_macro_name(macro_node, old_macro, new_macro)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_(new_macro))

    def test_that_GIVEN_xml_without_specified_macros_THEN_macros_are_not_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="PORT1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro_name = "BAUD1"
        new_macro_name = "BAUD"

        # When:
        self.macro_changer._change_macro_name(macro_node, old_macro_name, new_macro_name)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_("PORT1"))

    def test_that_GIVEN_xml_with_macro_matching_a_REGEX_THEN_macros_are_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="GALILADDR01", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro_name = r'GALILADDR([\d]{2})'
        new_macro_name = "GALILADDR"

        # When:
        self.macro_changer._change_macro_name(macro_node, old_macro_name, new_macro_name)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_(new_macro_name))


class TestChangMacroValue(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_old_ioc_macro_value_THEN_macro_values_are_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="BAUD1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro_value = "None"
        new_macro_value = "new"

        # When:
        self.macro_changer._change_macro_value(macro_node, old_macro_value, new_macro_value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(new_macro_value))

    def test_that_GIVEN_xml_without_specified_macro_value_THEN_macros_are_not_updated(self):
        # Given:
        original_macro_value = "None"
        test_macro_xml_string = MACRO_XML.format(name="PORT1", value=original_macro_value)
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro_value = "old"
        new_macro_value = "new"

        # When:
        self.macro_changer._change_macro_value(macro_node, old_macro_value, new_macro_value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(original_macro_value))

    def test_that_GIVEN_xml_old_macro_value_of_None_THEN_macro_values_are_not_updated(self):
        # Given:
        original_macro_value = "None"
        test_macro_xml_string = MACRO_XML.format(name="PORT1", value=original_macro_value)
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro_value = None
        new_macro_value = "new"

        # When:
        self.macro_changer._change_macro_value(macro_node, old_macro_value, new_macro_value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(original_macro_value))


class TestMacroChangesWithMultipleInputs(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_single_macro_WHEN_calling_change_macros_THEN_the_single_macro_is_updated(self):
        # Given:
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDRXX": ""}))
        macro_to_change = [{
            "ioc_name": "GALIL",
            "old_macro": ("GALILADDRXX", ""),
            "new_macro": ("GALILADDR", "")
        }]
        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.is_dir = Mock(return_value=True)
        self.file_access.listdir = Mock(return_value=["file1.xml"])

        # When:
        self.macro_changer.change_macro(macro_to_change)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result = written_xml.findall(".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE})

        assert_that(result, has_length(1), "changed macro count")
        assert_that(result[0].get("name"), is_("GALILADDR"))

    def test_that_GIVEN_xml_with_multiple_old_ioc_macros_THEN_all_macros_are_updated(self):
        # Given:
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDRXX": "", "MTRCTRLXX": ""}))
        macro_to_change = [{
                "ioc_name": "GALIL",
                "old_macro": ("GALILADDRXX", ""),
                "new_macro": ("GALILADDR", "1")
            },
            {
                "ioc_name": "GALIL",
                "old_macro": ("MTRCTRLXX", ""),
                "new_macro": ("MTRCTRL", "1")
            }]
        self.file_access.write_file_contents = xml

        self.file_access.open_file = Mock(return_value=self.file_access.write_file_contents)
        self.file_access.write_file = Mock()
        self.file_access.is_dir = Mock(return_value=True)
        self.file_access.listdir = Mock(return_value=["file1.xml"])

        # When:
        self.macro_changer.change_macro(macro_to_change)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result_galiladdr = written_xml.findall(".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE})
        result_mtrctrl = written_xml.findall(".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE})

        assert_that(result_mtrctrl, has_length(1), "changed macro count")
        assert_that(result_mtrctrl[0].get("name"), is_("MTRCTRL"))
        assert_that(result_mtrctrl[0].get("value"), is_("1"))

        assert_that(result_galiladdr, has_length(1), "changed macro count")
        assert_that(result_galiladdr[0].get("name"), is_("GALILADDR"))
        assert_that(result_galiladdr[0].get("value"), is_("1"))


if __name__ == '__main__':
    unittest.main()
