import unittest
from hamcrest import *
from mock import MagicMock as Mock
from xml.parsers.expat import ExpatError

from src.common_upgrades.add_to_base_iocs import AddToBaseIOCs, ALREADY_CONTAINS, FILE_TO_CHECK_STR, ADD_AFTER_MISSING
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs


TEST_XML_TO_ADD = """\
    <ioc autostart="true" name="TO_ADD" restart="true" simlevel="none">
        <macros/>
        <pvs/>
        <pvsets/>
    </ioc>
"""


class TestAddToBaseIOCs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()

    def test_GIVEN_no_ioc_xml_file_WHEN_adding_ioc_THEN_error(self):
        self.file_access.open_xml_file = Mock(side_effect=IOError("No configs Exist"))
        adder = AddToBaseIOCs(None, None, None)

        result = adder.perform(self.file_access, self.logger)

        assert_that(result, is_(-1), "result")
        assert_that(self.logger.log_err, has_item("Can not find file to modify in config."))

    def test_GIVEN_invalid_xml_WHEN_adding_ioc_THEN_error(self):
        error_str = "No configs Exist"
        self.file_access.open_xml_file = Mock(side_effect=ExpatError(error_str))
        adder = AddToBaseIOCs(None, None, None)

        result = adder.perform(self.file_access, self.logger)

        assert_that(result, is_(-1), "result")
        assert_that(self.logger.log_err, has_item("IOC file appears not be valid XML, error '{}'".format(error_str)))

    def test_GIVEN_xml_with_no_iocs_WHEN_get_ioc_names_THEN_empty_list(self):
        xml = create_xml_with_iocs(list())

        result = AddToBaseIOCs._get_ioc_names(xml)

        assert_that(result, is_(list()), "result")

    def test_GIVEN_xml_with_one_ioc_WHEN_get_ioc_names_THEN_single_ioc_name(self):
        ioc_names = ["TEST_NAME"]
        xml = create_xml_with_iocs(ioc_names)

        result = AddToBaseIOCs._get_ioc_names(xml)

        assert_that(result, is_(ioc_names), "result")

    def test_GIVEN_xml_with_two_ioc_WHEN_get_ioc_names_THEN_single_ioc_name(self):
        ioc_names = ["TEST_NAME", "TEST_NAME_2"]
        xml = create_xml_with_iocs(ioc_names)

        result = AddToBaseIOCs._get_ioc_names(xml)

        assert_that(result, is_(ioc_names), "result")

    def _assert_prerequiste_fails(self, adder, xml, expected_message):
        result = adder._check_prerequistes_for_file(xml, self.logger)

        assert_that(result, is_(False), "result")
        assert_that(self.logger.log_err, has_item(expected_message))

    def test_GIVEN_xml_already_containing_ioc_to_add_WHEN_checking_prerequisites_THEN_error(self):
        ioc_to_add = "TO_ADD"
        xml = create_xml_with_iocs(["ANOTHER_IOC", ioc_to_add])

        adder = AddToBaseIOCs(ioc_to_add, "", "")

        self._assert_prerequiste_fails(adder, xml, ALREADY_CONTAINS.format(FILE_TO_CHECK_STR, ioc_to_add))

    def test_GIVEN_xml_already_containing_two_ioc_to_add_WHEN_checking_prerequisites_THEN_error(self):
        ioc_to_add = "TO_ADD"
        xml = create_xml_with_iocs([ioc_to_add, "ANOTHER_IOC", ioc_to_add])

        adder = AddToBaseIOCs(ioc_to_add, "", "")

        self._assert_prerequiste_fails(adder, xml, ALREADY_CONTAINS.format(FILE_TO_CHECK_STR, ioc_to_add))

    def test_GIVEN_xml_containing_no_ioc_to_add_after_WHEN_checking_prerequisites_THEN_error(self):
        after_ioc = "AFTER_THIS"
        xml = create_xml_with_iocs(["ANOTHER_IOC", "SECOND_IOC"])

        adder = AddToBaseIOCs("", after_ioc, "")
        self._assert_prerequiste_fails(adder, xml, ADD_AFTER_MISSING.format(FILE_TO_CHECK_STR, 0, after_ioc))

    def test_GIVEN_xml_containing_two_ioc_to_add_after_WHEN_checking_prerequisites_THEN_error(self):
        after_ioc = "AFTER_THIS"
        xml = create_xml_with_iocs([after_ioc, "ANOTHER_IOC", after_ioc])

        adder = AddToBaseIOCs("", after_ioc, "")
        self._assert_prerequiste_fails(adder, xml, ADD_AFTER_MISSING.format(FILE_TO_CHECK_STR, 2, after_ioc))

    def test_GIVEN_xml_containing_ioc_to_add_after_and_no_ioc_to_add_WHEN_checking_prerequisites_THEN_passes(self):
        ioc_to_add = "TO_ADD"
        after_ioc = "AFTER_THIS"
        xml = create_xml_with_iocs(["ANOTHER_IOC", after_ioc, "SECOND_IOC"])

        adder = AddToBaseIOCs(ioc_to_add, after_ioc, "")
        result = adder._check_prerequistes_for_file(xml, self.logger)

        assert_that(result, is_(True), "result")

    def test_GIVEN_xml_containing_no_ioc_to_add_after_WHEN_add_ioc_THEN_error(self):
        ioc_to_add = "TO_ADD"
        after_ioc = "AFTER_THIS"
        xml = create_xml_with_iocs(["ANOTHER_IOC", "SECOND_IOC"])

        adder = AddToBaseIOCs(ioc_to_add, after_ioc, "")
        result = adder._add_ioc(xml, self.logger)

        assert_that(result, is_(xml), "xml changed despite error")
        assert_that(self.logger.log_err, has_item("Could not find {0} ioc in file so no {1} ioc added.".format(
            after_ioc, ioc_to_add)))

    def test_GIVEN_xml_containing_ioc_to_add_after_WHEN_add_ioc_THEN_ioc_added(self):
        ioc_to_add = "TO_ADD"
        after_ioc = "AFTER_THIS"
        xml = create_xml_with_iocs([after_ioc, "ANOTHER_IOC"])

        adder = AddToBaseIOCs(ioc_to_add, after_ioc, TEST_XML_TO_ADD)

        result = adder._add_ioc(xml, self.logger)

        iocs = result.getElementsByTagName("ioc")

        assert_that(len(iocs), is_(3), "ioc added")

        assert_that(iocs[1].getAttribute("name"), is_(ioc_to_add), "correctly named ioc added")
        [assert_that(iocs[1].hasAttribute(attr), "correct xml added") for attr in ["restart", "autostart", "simlevel"]]


if __name__ == '__main__':
    unittest.main()
