import unittest
from hamcrest import *
from functools import partial
from src.common_upgrades.config_filter import ConfigFilter
from test.mother import LoggingStub, FileAccessStub, create_xml_with_iocs


def generate_many_iocs(configs):
    for config, iocs in configs.items():
        yield (config, create_xml_with_iocs(iocs))


class TestAddToBaseIOCs(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.filter = ConfigFilter(self.file_access, self.logger)

    def test_GIVEN_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)

        assert_that(len(list(result)), is_(0), "no results")

    def test_GIVEN_two_xml_with_no_requested_iocs_WHEN_filtering_THEN_no_iocs_returned(self):
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"], "CONFIG_2": ["OTHER_IOC"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)

        assert_that(len(list(result)), is_(0), "no results")

    def test_GIVEN_xml_with_requested_iocs_WHEN_filtering_THEN_expected_ioc_returned(self):
        ioc_to_change = "CHANGE_ME"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_to_change, "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)

        result = list(result)
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_GIVEN_one_xml_with_requested_iocs_and_one_without_WHEN_filtering_THEN_only_expected_ioc_returned(self):
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        configs = {good_config: [ioc_to_change, "ANOTHER_ONE"], "CONFIG_2": ["DONT_CHANGE", "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)

        result = list(result)
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_to_change))

    def test_GIVEN_xml_with_requested_ioc_WHEN_after_filtering_THEN_ioc_saved_to_file(self):
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        configs = {good_config: [ioc_to_change, "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)
        list(result)  # Get all values out of generator

        assert_that(self.file_access.write_filename, is_(good_config))
        expected_xml = create_xml_with_iocs(configs[good_config]).toxml()
        assert_that(self.file_access.write_file_contents, is_(expected_xml))

    def test_GIVEN_xml_with_no_requested_ioc_WHEN_after_filtering_THEN_ioc_not_saved_to_file(self):
        ioc_to_change = "CHANGE_ME"
        configs = {"CONFIG_1": ["DONT_CHANGE", "ANOTHER_ONE"], "CONFIG_2": ["OTHER_IOC"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)
        list(result)  # Get all values out of generator

        assert_that(self.file_access.write_filename, is_(None))
        assert_that(self.file_access.write_file_contents, is_(None))

    def test_GIVEN_xml_with_requested_ioc_WHEN_changed_after_filtering_THEN_changed_xml_written(self):
        ioc_to_change = "CHANGE_ME"
        good_config = "CONFIG_1"
        new_attr = "TEST_ATTR"
        configs = {good_config: [ioc_to_change, "ANOTHER_ONE"], "CONFIG_2": ["DONT_CHANGE", "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(ioc_to_change)

        ioc = next(result)
        ioc.setAttribute(new_attr, "test")
        assert_that(calling(next).with_args(result), raises(StopIteration), "only one result")

        assert_that(self.file_access.write_filename, is_(good_config))
        assert_that(self.file_access.write_file_contents, contains_string(new_attr))

    def test_GIVEN_xml_with_numbered_ioc_WHEN_filtering_THEN_expected_ioc_returned(self):
        root_ioc_name = "CHANGE_ME"
        ioc_name = root_ioc_name + "_03"
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(root_ioc_name)

        result = list(result)
        assert_that(len(result), is_(1))
        assert_that(result[0].getAttribute("name"), is_(ioc_name))

    def test_GIVEN_xml_with_ioc_containing_requested_WHEN_filtering_THEN_nothing_returned(self):
        root_ioc_name = "CHANGE_ME"
        ioc_name = "PRE-{}-POST".format(root_ioc_name)
        config_name = "CONFIG_1"
        configs = {config_name: [ioc_name, "ANOTHER_ONE"]}

        self.filter.ioc_file_generator = partial(generate_many_iocs, configs)
        result = self.filter.ioc_filter_generator(root_ioc_name)

        result = list(result)
        assert_that(len(result), is_(0))


if __name__ == '__main__':
    unittest.main()
