import unittest
from hamcrest import *
from mock import MagicMock as Mock

import xml.etree.ElementTree as ET

from src.upgrade_step_from_4p1p0 import UpgradeStepFrom4p1p0
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


def create_galil_ioc(galil_num, macros):
    macro_xml = "".join([MACRO_XML.format(name=name, value=value) for name, value in macros.items()])
    return IOC_XML.format(name="GALIL_{:0>2}".format(galil_num), macros=macro_xml)



class TestUpgradeStepFrom4p1p0(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom4p1p0()
        self.logger = LoggingStub()

    def test_GIVEN_galiladdr_and_mtrctrl_already_present_WHEN_replaced_THEN_warning_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR": "", "MTRCTRL": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(2), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(0), "Contains error {}".format(self.logger.log_err))

        assert_that(self.file_access.write_file_contents, is_(xml))

    def test_GIVEN_galiladdr_already_present_and_mtrctrl_not_present_WHEN_replaced_THEN_error_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(1), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(1), "Contains error {}".format(self.logger.log_err))

        assert_that(self.file_access.write_file_contents, is_(xml))

    def test_GIVEN_old_galiladdr_present_and_mtrctrl_present_WHEN_replaced_THEN_error_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": "", "MTRCTRL": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(1), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(1), "Contains error {}".format(self.logger.log_err))

        assert_that(self.file_access.write_file_contents, is_(xml))

    def test_GIVEN_multiple_old_galiladdr_present_WHEN_replaced_THEN_error_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": "", "GALILADDR02": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(1), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(1), "Contains error {}".format(self.logger.log_err))

        assert_that(self.file_access.write_file_contents, is_(xml))

    def test_GIVEN_old_galilarr01_WHEN_replaced_THEN_mtrcrtl_contains_01(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        written_xml = ET.fromstring(self.file_access.write_file_contents)
        mtrctrl_xml = written_xml.findall(".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE})

        assert_that(len(mtrctrl_xml), is_(1))
        assert_that(mtrctrl_xml[0].get("value"), is_("01"))

    def test_GIVEN_old_galilarr03_WHEN_replaced_THEN_mtrcrtl_contains_03(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR03": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        written_xml = ET.fromstring(self.file_access.write_file_contents)
        mtrctrl_xml = written_xml.findall(".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE})

        assert_that(len(mtrctrl_xml), is_(1))
        assert_that(mtrctrl_xml[0].get("value"), is_("03"))


if __name__ == '__main__':
    unittest.main()
