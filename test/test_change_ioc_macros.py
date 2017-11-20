import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.common_upgrades.change_ioc_macros import ChangeIOCMacros
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs


def generate_many_iocs(configs):
    return ((config, create_xml_with_iocs(iocs)) for config, iocs in configs.items())


class TestAddToBaseIOCs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()

    def test_GIVEN_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"]}
        self.file_access.ioc_file_generator = generate_many_iocs(configs)

        changer = ChangeIOCMacros(self.file_access, ioc_to_change)

        assert_that(len(changer.iocs_in_configs), is_(0), "no results")

    def test_GIVEN_two_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"], "CONFIG_2": ["OTHER_IOC"]}
        self.file_access.ioc_file_generator = generate_many_iocs(configs)

        changer = ChangeIOCMacros(self.file_access, ioc_to_change)

        assert_that(len(changer.iocs_in_configs), is_(0), "no results")

    def test_GIVEN_xml_with_requested_iocs_WHEN_filtering_THEN_ioc_xml_returned(self):
        ioc_to_change = "CHANGE_ME"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_to_change, "ANOTHER_ONE"]}
        self.file_access.ioc_file_generator = generate_many_iocs(configs)

        changer = ChangeIOCMacros(self.file_access, ioc_to_change)

        assert_that(len(changer.iocs_in_configs), is_(1), "no results")
        assert_that(config_name in changer.iocs_in_configs.keys())
        expected_xml = create_xml_with_iocs(configs[config_name]).toprettyxml()
        assert_that(changer.iocs_in_configs[config_name].toprettyxml(), is_(expected_xml))

    def test_GIVEN_one_xml_with_requested_iocs_and_one_without_WHEN_filtering_THEN_only_xml_with_ioc_returned(self):
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        configs = {good_config: [ioc_to_change, "ANOTHER_ONE"], "CONFIG_2": ["DONT_CHANGE", "ANOTHER_ONE"]}
        self.file_access.ioc_file_generator = generate_many_iocs(configs)

        changer = ChangeIOCMacros(self.file_access, ioc_to_change)

        assert_that(len(changer.iocs_in_configs), is_(1), "no results")
        assert_that(good_config in changer.iocs_in_configs.keys())
        expected_xml = create_xml_with_iocs(configs[good_config]).toprettyxml()
        assert_that(changer.iocs_in_configs[good_config].toprettyxml(), is_(expected_xml))


if __name__ == '__main__':
    unittest.main()
