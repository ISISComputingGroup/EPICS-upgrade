import unittest
from hamcrest import *
from functools import partial
from src.common_upgrades.xml_macro_changer import XMLMacroChanger
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs
from xml.dom import minidom

MACRO_XML = """
        <macro name="{name}" value="{value}"/>
        """


def generate_many_iocs(configs):
    for config, iocs in configs.items():
        yield (config, create_xml_with_iocs(iocs))


class TestTagGenerator(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = XMLMacroChanger(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        # Given:
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, ioc_to_change)))

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
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, ioc_to_change)))

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
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, ioc_to_change)))

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
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, ioc_to_change)))

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
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, root_ioc_name)))

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
            result.extend(list(self.macro_changer._ioc_tag_generator(config, xml, root_ioc_name)))

        # Then:
        assert_that(len(result), is_(0))


class TestMacroChanger(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = XMLMacroChanger(self.file_access, self.logger)

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
        assert_that(result, new_macro)

    def test_that_GIVEN_xml_without_specified_ioc_macros_THEN_macros_are_not_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = "BAUD1"
        new_macro = "PORT"

        # When:
        self.macro_changer._change_macro_name(macro_node, old_macro, new_macro)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, new_macro)


if __name__ == '__main__':
    unittest.main()
