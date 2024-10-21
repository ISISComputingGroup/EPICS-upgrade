import unittest
import xml.etree.ElementTree as ET
from functools import partial
from xml.dom import minidom

from hamcrest import *
from mock import MagicMock as Mock

from src.common_upgrades.change_macros_in_xml import (
    ChangeMacrosInXML,
    change_macro_name,
    change_macro_value,
)
from src.common_upgrades.utils.macro import Macro
from test.mother import FileAccessStub, LoggingStub, create_xml_with_iocs

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

SYNOPTIC_FILE_XML = """<?xml version="1.0" ?>
<instrument xmlns="http://www.isis.stfc.ac.uk//instrument">
    {synoptics}
</instrument>
"""

SYOPTIC_XML = """<name>Goniometer</name>
    <components>
        <component>
            <name>New Component</name>
            <type>GONIOMETER</type>
            <target>
                <name>Device</name>
                <type>OPI</type>
                <properties>
                    <property>
                        <value>{0}</value>
                    </property>
                </properties>
            </target>
            <pvs/>
            <components/>
        </component>
    </components>
"""


MACRO_XML = """
        <macro name="{name}" value="{value}"/>
        """


def generate_many_iocs(configs):
    for config, iocs in configs.items():
        yield config, create_xml_with_iocs(iocs)


def create_galil_ioc(galil_num, macros):
    macro_xml = "".join(
        [MACRO_XML.format(name=name, value=value) for name, value in macros.items()]
    )
    return IOC_XML.format(name="GALIL_{:0>2}".format(galil_num), macros=macro_xml)


class TestTagGenerator(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(
        self,
    ):
        # Given:
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change))
            )

        # Then:
        assert_that(len(list(result)), is_(0), "no results")

    def test_that_GIVEN_two_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(
        self,
    ):
        # Given:
        ioc_to_change = "CHANGE_ME"
        configs = {
            "CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"],
            "CONFIG_2": ["OTHER_IOC"],
        }

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change))
            )

        # Then:
        assert_that(len(list(result)), is_(0), "no results")

    def test_that_GIVEN_xml_with_requested_iocs_WHEN_filtering_THEN_expected_ioc_returned(
        self,
    ):
        # Given:
        ioc_to_change = "CHANGE_ME"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_to_change, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change))
            )

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_that_GIVEN_one_xml_with_requested_iocs_and_one_without_WHEN_filtering_THEN_only_expected_ioc_returned(
        self,
    ):
        # Given:
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        configs = {
            good_config: [ioc_to_change, "ANOTHER_ONE"],
            "CONFIG_2": ["DONT_CHANGE", "ANOTHER_ONE"],
        }

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, ioc_to_change))
            )

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_that_GIVEN_xml_with_numbered_ioc_WHEN_filtering_THEN_expected_ioc_returned(
        self,
    ):
        # Given
        root_ioc_name = "CHANGE_ME"
        ioc_name = root_ioc_name + "_03"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, root_ioc_name))
            )

        # Then:
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_name))

    def test_that_GIVEN_xml_with_ioc_containing_requested_WHEN_filtering_THEN_nothing_returned(
        self,
    ):
        # Given:
        root_ioc_name = "CHANGE_ME"
        ioc_name = "PRE-{}-POST".format(root_ioc_name)
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        # When:
        self.macro_changer._ioc_file_generator = partial(generate_many_iocs, configs)
        result = []
        for config, xml in self.macro_changer._ioc_file_generator():
            result.extend(
                list(self.macro_changer.ioc_tag_generator(config, xml, root_ioc_name))
            )

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
        change_macro_name(macro_node, old_macro, new_macro)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_(new_macro))

    def test_that_GIVEN_xml_without_specified_macros_THEN_macros_are_not_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="PORT1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = Macro("BAUD1")
        new_macro = Macro("BAUD")

        # When:
        change_macro_name(macro_node, old_macro.name, new_macro.name)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_("PORT1"))

    def test_that_GIVEN_xml_with_macro_matching_a_REGEX_THEN_macros_are_updated(self):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="GALILADDR01", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = Macro(r"GALILADDR([\d]{2})")
        new_macro = Macro("GALILADDR")

        # When:
        change_macro_name(macro_node, old_macro.name, new_macro.name)
        result = macro_node.getAttribute("name")

        # Then:
        assert_that(result, is_(new_macro.name))


class TestChangMacroValue(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_old_ioc_macro_value_THEN_macro_values_are_updated(
        self,
    ):
        # Given:
        test_macro_xml_string = MACRO_XML.format(name="BAUD1", value="None")
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = Macro("BAUD1", "None")
        new_macro = Macro("BAUD1", "new")

        # When:
        change_macro_value(macro_node, old_macro.value, new_macro.value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(new_macro.value))

    def test_that_GIVEN_xml_without_specified_macro_value_THEN_macros_are_not_updated(
        self,
    ):
        # Given:
        original_macro_value = "None"
        test_macro_xml_string = MACRO_XML.format(
            name="PORT1", value=original_macro_value
        )
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = Macro("PORT1", "old")
        new_macro = Macro("PORT1", "new")

        # When:
        change_macro_value(macro_node, old_macro.value, new_macro.value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(original_macro_value))

    def test_that_GIVEN_new_macro_without_a_value_THEN_macro_values_are_not_updated(
        self,
    ):
        # Given:
        original_macro_value = "None"
        test_macro_xml_string = MACRO_XML.format(
            name="PORT1", value=original_macro_value
        )
        test_macro_xml = minidom.parseString(test_macro_xml_string)
        macro_node = test_macro_xml.getElementsByTagName("macro")[0]
        old_macro = Macro("PORT1", "new")
        new_macro = Macro("PORT1")

        # When:
        change_macro_value(macro_node, old_macro.value, new_macro.value)
        result = macro_node.getAttribute("value")

        # Then:
        assert_that(result, is_(original_macro_value))


class TestMacroChangesWithMultipleInputs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_that_GIVEN_xml_with_single_macro_WHEN_calling_change_macros_THEN_the_single_macro_is_updated(
        self,
    ):
        # Given:
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDRXX": ""}))
        ioc_name = "GALIL"
        macro_to_change = [(Macro("GALILADDRXX"), Macro("GALILADDR"))]

        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_macros(ioc_name, macro_to_change)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result = written_xml.findall(
            ".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE}
        )

        assert_that(result, has_length(1), "changed macro count")
        assert_that(result[0].get("name"), is_("GALILADDR"))

    def test_that_GIVEN_xml_with_multiple_macros_THEN_only_value_of_named_macro_is_changed(
        self,
    ):
        # Given:
        xml = IOC_FILE_XML.format(
            iocs=create_galil_ioc(1, {"GALILADDR": "0", "MTRCTRL": "0"})
        )
        ioc_name = "GALIL"
        macro_to_change = [(Macro("GALILADDR"), Macro("GALILADDR", "1"))]

        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_macros(ioc_name, macro_to_change)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result_galiladdr = written_xml.findall(
            ".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE}
        )
        result_mtrctrl = written_xml.findall(
            ".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE}
        )

        assert_that(result_galiladdr, has_length(1), "changed macro count")
        assert_that(result_galiladdr[0].get("name"), is_("GALILADDR"))
        assert_that(result_galiladdr[0].get("value"), is_("1"))

        assert_that(result_mtrctrl, has_length(1), "changed macro count")
        assert_that(result_mtrctrl[0].get("name"), is_("MTRCTRL"))
        assert_that(result_mtrctrl[0].get("value"), is_("0"))

    def test_that_GIVEN_xml_with_multiple_old_ioc_macros_THEN_all_macros_are_updated(
        self,
    ):
        # Given:
        xml = IOC_FILE_XML.format(
            iocs=create_galil_ioc(1, {"GALILADDRXX": "", "MTRCTRLXX": ""})
        )
        ioc_name = "GALIL"
        macros_to_change = [
            (Macro("GALILADDRXX", ""), Macro("GALILADDR", "1")),
            (Macro("MTRCTRLXX", ""), Macro("MTRCTRL", "1")),
        ]
        self.file_access.write_file_contents = xml

        self.file_access.open_file = Mock(
            return_value=self.file_access.write_file_contents
        )
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_macros(ioc_name, macros_to_change)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result_galiladdr = written_xml.findall(
            ".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE}
        )
        result_mtrctrl = written_xml.findall(
            ".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE}
        )

        assert_that(result_mtrctrl, has_length(1), "changed macro count")
        assert_that(result_mtrctrl[0].get("name"), is_("MTRCTRL"))
        assert_that(result_mtrctrl[0].get("value"), is_("1"))

        assert_that(result_galiladdr, has_length(1), "changed macro count")
        assert_that(result_galiladdr[0].get("name"), is_("GALILADDR"))
        assert_that(result_galiladdr[0].get("value"), is_("1"))


class TestChangeIOCName(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def create_synoptic_file_with_multiple_IOCs(self, iocs):
        """Mocks out a synoptic file with multiple IOCs in it.

        Args:
            iocs: List of strings with the IOC names in it

        Returns:
            formatted_synoptic_file: A mock XML document containing a sample synoptic

        """
        synoptics = "".join([SYOPTIC_XML.format(ioc) for ioc in iocs])
        formatted_synoptic_file = SYNOPTIC_FILE_XML.format(synoptics=synoptics)

        return formatted_synoptic_file

    def test_GIVEN_an_ioc_name_WHEN_IOC_change_asked_THEN_ioc_name_is_changed(self):
        # Given:
        ioc_suffix_digit = 1
        xml = IOC_FILE_XML.format(
            iocs=create_galil_ioc(ioc_suffix_digit, {"GALILADDRXX": ""})
        )

        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_ioc_name("GALIL", "CHANGED")

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        tree = ET.ElementTree(written_xml)

        iocs = tree.findall(".//ns:ioc", {"ns": NAMESPACE})

        assert_that(iocs[0].get("name"), is_("CHANGED_{:02}".format(ioc_suffix_digit)))

    def test_GIVEN_more_than_one_IOC_in_config_WHEN_its_name_is_changed_THEN_IOC_suffix_digits_are_preserved(
        self,
    ):
        # Given:
        number_of_repeated_iocs = 3

        ioc_to_change = "CHANGEME"
        new_ioc_name = "CHANGED"

        ioc_names = [
            "{}_{:02d}".format(ioc_to_change, i)
            for i in range(1, number_of_repeated_iocs + 1)
        ]
        new_ioc_names = [
            "{}_{:02d}".format(new_ioc_name, i)
            for i in range(1, number_of_repeated_iocs + 1)
        ]

        xml_contents = create_xml_with_iocs(ioc_names).toxml()

        self.file_access.open_file = Mock(return_value=xml_contents)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_ioc_name(ioc_to_change, new_ioc_name)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        tree = ET.ElementTree(written_xml)
        iocs = tree.findall(".//ioc", {"ns": NAMESPACE})

        for repeated_ioc_index, ioc in enumerate(iocs):
            assert_that(ioc.get("name"), is_(new_ioc_names[repeated_ioc_index]))

    def test_GIVEN_multiple_different_IOCs_in_configuration_WHEN_ones_name_is_changed_THEN_only_that_ioc_changes(
        self,
    ):
        # Given:
        number_of_repeated_iocs = 3

        ioc_to_change = "CHANGEME"
        new_ioc_name = "CHANGED"

        all_ioc_names = ["CHANGEME", "GALIL", "DONTCHANGE"]

        ioc_names = []
        new_ioc_names = []

        for ioc in all_ioc_names:
            for repeat_suffix in range(1, number_of_repeated_iocs + 1):
                ioc_names.append("{}_{:02d}".format(ioc, repeat_suffix))

                if ioc == ioc_to_change:
                    new_ioc_names.append(
                        "{}_{:02d}".format(new_ioc_name, repeat_suffix)
                    )
                else:
                    new_ioc_names.append("{}_{:02d}".format(ioc, repeat_suffix))

        xml_contents = create_xml_with_iocs(ioc_names).toxml()

        self.file_access.open_file = Mock(return_value=xml_contents)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.change_ioc_name(ioc_to_change, new_ioc_name)

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        tree = ET.ElementTree(written_xml)
        iocs = tree.findall(".//ioc", {"ns": NAMESPACE})

        for i, ioc in enumerate(iocs):
            assert_that(ioc.get("name"), is_(new_ioc_names[i]))

    def test_GIVEN_synoptic_xml_file_WHEN_IOC_name_changed_THEN_only_the_ioc_synoptics_are_changed(
        self,
    ):
        # Given:
        ioc_to_change = "CHANGEME"
        new_ioc_name = "CHANGED"
        unchanged_ioc = "DONTCHANGE"

        suffix = "_01"

        synoptic_file = self.create_synoptic_file_with_multiple_IOCs(
            [ioc_to_change + suffix, unchanged_ioc + suffix]
        )

        self.file_access.open_file = Mock(return_value=synoptic_file)
        self.file_access.is_dir = Mock(return_value=True)
        self.file_access.listdir = Mock(return_value=["file1.xml"])

        # When:
        self.macro_changer.change_ioc_name_in_synoptics(ioc_to_change, new_ioc_name)

        # Then:
        output_file = self.file_access.write_file_contents

        assert_that((ioc_to_change in output_file), is_(False))
        assert_that((new_ioc_name in output_file), is_(True))
        assert_that((unchanged_ioc in output_file), is_(True))


class TestAddMacro(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.macro_changer = ChangeMacrosInXML(self.file_access, self.logger)

    def test_GIVEN_one_ioc_THEN_add_macro(self):
        # Given:
        xml = IOC_FILE_XML.format(
            iocs=create_galil_ioc(1, {"GALILADDR": "0", "MTRCTRL": "0"})
        )
        ioc_name = "GALIL"
        macro_to_add = Macro("TEST", "1")
        pattern = "^(0|1)$"
        description = "Test description"
        default = "0"

        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.add_macro(
            ioc_name, macro_to_add, pattern, description, default
        )

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result_galiladdr = written_xml.findall(
            ".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE}
        )
        result_mtrctrl = written_xml.findall(
            ".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE}
        )
        result_test = written_xml.findall(
            ".//ns:macros/*[@name='TEST']", {"ns": NAMESPACE}
        )

        assert_that(result_galiladdr, has_length(1), "changed macro count")
        assert_that(result_galiladdr[0].get("name"), is_("GALILADDR"))
        assert_that(result_galiladdr[0].get("value"), is_("0"))

        assert_that(result_mtrctrl, has_length(1), "changed macro count")
        assert_that(result_mtrctrl[0].get("name"), is_("MTRCTRL"))
        assert_that(result_mtrctrl[0].get("value"), is_("0"))

        assert_that(result_test, has_length(1), "changed macro count")
        assert_that(result_test[0].get("name"), is_(macro_to_add.name))
        assert_that(result_test[0].get("value"), is_(macro_to_add.value))

    def test_GIVEN_one_ioc_that_already_has_macro_THEN_dont_add_macro(self):
        # Given:
        xml = IOC_FILE_XML.format(
            iocs=create_galil_ioc(1, {"GALILADDR": "0", "MTRCTRL": "0", "TEST": "0"})
        )
        ioc_name = "GALIL"
        macro_to_add = Macro("TEST", "1")
        pattern = "^(0|1)$"
        description = "Test description"
        default = "0"

        self.file_access.open_file = Mock(return_value=xml)
        self.file_access.write_file = Mock()
        self.file_access.get_config_files = Mock(
            return_value=[("file1.xml", self.file_access.open_xml_file(None))]
        )

        # When:
        self.macro_changer.add_macro(
            ioc_name, macro_to_add, pattern, description, default
        )

        # Then:
        written_xml = ET.fromstring(self.file_access.write_file_contents)
        result_galiladdr = written_xml.findall(
            ".//ns:macros/*[@name='GALILADDR']", {"ns": NAMESPACE}
        )
        result_mtrctrl = written_xml.findall(
            ".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE}
        )
        result_test = written_xml.findall(
            ".//ns:macros/*[@name='TEST']", {"ns": NAMESPACE}
        )

        assert_that(result_galiladdr, has_length(1), "changed macro count")
        assert_that(result_galiladdr[0].get("name"), is_("GALILADDR"))
        assert_that(result_galiladdr[0].get("value"), is_("0"))

        assert_that(result_mtrctrl, has_length(1), "changed macro count")
        assert_that(result_mtrctrl[0].get("name"), is_("MTRCTRL"))
        assert_that(result_mtrctrl[0].get("value"), is_("0"))

        assert_that(result_test, has_length(1), "changed macro count")
        assert_that(result_test[0].get("name"), is_("TEST"))
        assert_that(result_test[0].get("value"), is_("0"))


if __name__ == "__main__":
    unittest.main()
