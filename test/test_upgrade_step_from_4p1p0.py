import unittest
from hamcrest import *
from mock import MagicMock as Mock
from mock import call
import xml.etree.ElementTree as ET
import os
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

TEST_STRING = "Test {} inside a line"

def create_galil_ioc(galil_num, macros):
    macro_xml = "".join([MACRO_XML.format(name=name, value=value) for name, value in macros.items()])
    return IOC_XML.format(name="GALIL_{:0>2}".format(galil_num), macros=macro_xml)


class TestUpgradeStepFrom4p1p0(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom4p1p0()
        self.logger = LoggingStub()

    def test_GIVEN_a_file_in_the_configuration_directory_WHEN_searched_THEN_it_is_not_opened(self):
        self.file_access.open_file = Mock()
        self.file_access.is_dir = Mock(return_value=False)

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        self.file_access.open_file.assert_not_called()

    def test_GIVEN_config_in_the_configuration_directory_WHEN_searched_THEN_ioc_file_opened(self):
        config_name = "TEST_CONFIG"
        self.file_access.open_file = Mock()
        self.file_access.is_dir = Mock(return_value=True)
        self.file_access.listdir = Mock(return_value=[config_name])

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        self.file_access.open_file.assert_called_once_with(os.path.join(config_name, "iocs.xml"))

    def test_GIVEN_galiladdr_and_mtrctrl_already_present_WHEN_replaced_THEN_warning_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR": "", "MTRCTRL": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(2), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(0), "Contains error {}".format(self.logger.log_err))

        assert_that(self.file_access.write_file_contents, is_(xml))

    def test_GIVEN_galiladdr_already_present_and_mtrctrl_not_present_WHEN_replaced_THEN_info_logged_and_nothing_saved(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.write_file = Mock()
        self.file_access.is_dir = Mock(return_value=True)
        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(2), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(0), "Contains error {}".format(self.logger.log_err))

        self.file_access.write_file.assert_not_called()

    def test_GIVEN_old_galiladdr_present_and_mtrctrl_present_WHEN_replaced_THEN_error_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": "", "MTRCTRL": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)
        self.file_access.write_file = Mock()

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(1), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(1), "Contains error {}".format(self.logger.log_err))

        self.file_access.write_file.assert_not_called()

    def test_GIVEN_multiple_old_galiladdr_present_WHEN_replaced_THEN_error_logged_and_no_change_made(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": "", "GALILADDR02": ""}))
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        assert_that(len(self.logger.log), is_(1), "Contains info {}".format(self.logger.log))
        assert_that(len(self.logger.log_err), is_(1), "Contains error {}".format(self.logger.log_err))

        self.file_access.write_file.assert_not_called()

    def test_GIVEN_old_galilarr01_WHEN_replaced_THEN_mtrcrtl_contains_01(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR01": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        written_xml = ET.fromstring(self.file_access.write_file_contents)
        mtrctrl_xml = written_xml.findall(".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE})

        assert_that(len(mtrctrl_xml), is_(1))
        assert_that(mtrctrl_xml[0].get("value"), is_("01"))

    def test_GIVEN_old_galilarr03_WHEN_replaced_THEN_mtrcrtl_contains_03(self):
        xml = IOC_FILE_XML.format(iocs=create_galil_ioc(1, {"GALILADDR03": ""}))
        self.file_access.open_file = Mock(side_effect=[xml, "<a/>"])
        self.file_access.is_dir = Mock(return_value=True)

        self.upgrade_step.change_ioc_macros(self.file_access, self.logger)

        written_xml = ET.fromstring(self.file_access.write_file_contents)
        mtrctrl_xml = written_xml.findall(".//ns:macros/*[@name='MTRCTRL']", {"ns": NAMESPACE})

        assert_that(len(mtrctrl_xml), is_(1))
        assert_that(mtrctrl_xml[0].get("value"), is_("03"))

    def test_WHEN_changed_cmd_files_THEN_loads_all_cmd_files(self):
        open_file_mock = Mock(return_value="")
        self.file_access.open_file = open_file_mock
        cmd_files = ["galil2.cmd", "galil10.cmd", "jaws.cmd"]
        files = ["other.o", "another.cmdp"] + cmd_files
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "gailil", f) for f in files])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(open_file_mock.call_args_list, is_(
            [call(os.path.join("configurations", "gailil", f)) for f in cmd_files]))

    def _set_up_galil_dir_and_change(self, cmd_files):
        self.file_access.open_file = Mock(return_value="")
        self.file_access.listdir = Mock(return_value=(["other.o", "another.cmdp"] + cmd_files))

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

    def test_GIVEN_galil1_cmd_WHEN_change_galil_files_THEN_saved_as_galil01_cmd(self):
        self._set_up_galil_dir_and_change(["galil1.cmd"])

        expected = os.path.join("configurations", "galil", "galil01.cmd")
        assert_that(self.file_access.write_filename, is_(expected))

    def test_GIVEN_galil5_cmd_WHEN_change_galil_files_THEN_saved_as_galil05_cmd(self):
        self._set_up_galil_dir_and_change(["galil5.cmd"])

        expected = os.path.join("configurations", "galil", "galil05.cmd")
        assert_that(self.file_access.write_filename, is_(expected))

    def test_GIVEN_galil10_cmd_WHEN_change_galil_files_THEN_saved_as_galil10_cmd(self):
        self._set_up_galil_dir_and_change(["galil10.cmd"])

        expected = os.path.join("configurations", "galil", "galil10.cmd")
        assert_that(self.file_access.write_filename, is_(expected))

    def test_GIVEN_two_galil_cmd_WHEN_change_cmd_files_THEN_both_saved_as_new_style(self):
        self.file_access.write_file = Mock()
        self._set_up_galil_dir_and_change(["galil2.cmd", "galil05.cmd"])

        expected = [os.path.join("configurations", "galil", f) for f in ["galil02.cmd", "galil05.cmd"]]
        assert_that([c[0][0] for c in self.file_access.write_file.call_args_list], is_(expected))

    def test_GIVEN_galil_cmd_containing_GALILADDR03_WHEN_change_galil_files_THEN_cmd_saved_with_GALILADDR(self):
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(return_value=[TEST_STRING.format("GALILADDR03")])
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "galil3.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(self.file_access.write_file.call_args[0][1], is_([TEST_STRING.format("GALILADDR")]))

    def test_GIVEN_galil_cmd_containing_GALILADDR10_WHEN_change_galil_files_THEN_cmd_saved_with_GALILADDR(self):
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(return_value=[TEST_STRING.format("GALILADDR10")])
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "galil3.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(self.file_access.write_file.call_args[0][1], is_([TEST_STRING.format("GALILADDR")]))

    def test_GIVEN_galil_cmd_containing_GALILADDR_WHEN_change_galil_files_THEN_cmd_unchanged(self):
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(return_value=[TEST_STRING.format("GALILADDR")])
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "galil3.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(self.file_access.write_file.call_args[0][1], is_([TEST_STRING.format("GALILADDR")]))

    def test_GIVEN_old_style_galil_cmd_WHEN_change_galil_files_THEN_old_cmd_removed(self):
        self.file_access.remove_file = Mock()
        old_cmd = os.path.join("galil", "galil3.cmd")
        self.file_access.open_file = Mock(return_value="")
        self.file_access.listdir = Mock(return_value=[old_cmd])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        self.file_access.remove_file.assert_called_with(old_cmd)

    def test_GIVEN_new_style_galil_cmd_WHEN_change_galil_files_THEN_cmd_not_removed(self):
        self.file_access.remove_file = Mock()
        self.file_access.open_file = Mock(return_value="")
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "galil10.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        self.file_access.remove_file.assert_not_called()

    def test_GIVEN_cmd_with_IFDMC01_WHEN_change_cmd_files_THEN_changed_to_IFIOC_GALIL_01(self):
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(return_value=[TEST_STRING.format("$(IFDMC01)")])
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "jaws.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(self.file_access.write_file.call_args[0][1], is_([TEST_STRING.format("$(IFIOC_GALIL_01)")]))

    def test_GIVEN_cmd_with_IFDMC15_WHEN_change_cmd_files_THEN_changed_to_IFIOC_GALIL_15(self):
        self.file_access.write_file = Mock()
        self.file_access.open_file = Mock(return_value=[TEST_STRING.format("$(IFDMC15)")])
        self.file_access.listdir = Mock(return_value=[os.path.join("configurations", "galil", "jaws.cmd")])

        self.upgrade_step.change_cmd_files(self.file_access, self.logger)

        assert_that(self.file_access.write_file.call_args[0][1], is_([TEST_STRING.format("$(IFIOC_GALIL_15)")]))

    def test_GIVEN_generic_cmd_WHEN_change_cmd_files_THEN_file_name_unchanged(self):
        filename = "jaws.cmd"
        self._set_up_galil_dir_and_change([filename])

        assert_that(self.file_access.write_filename, is_(filename))

if __name__ == '__main__':
    unittest.main()
