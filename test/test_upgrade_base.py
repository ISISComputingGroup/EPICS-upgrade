import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.upgrade import Upgrade, UpgradeError
from src.upgrade_step import UpgradeStep
from mother import LoggingStub, FileAccessStub


class TestUpgradeBase(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.first_version = "3.2.0"

    def upgrade(self, upgrade_steps=None):
        if upgrade_steps is None:
            upgrade_steps = [(self.first_version, None)]
        return Upgrade(self.file_access, self.logger, upgrade_steps)


    def test_GIVEN_config_contains_no_version_number_WHEN_load_THEN_version_number_added(self):
        self.file_access.open_file = Mock(side_effect=IOError("No configs Exist"))

        result = self.upgrade().get_version_number()

        assert_that(result, is_(self.first_version), "Version number")
        assert_that(self.file_access.wrote_version, is_(self.first_version))


    def test_GIVEN_config_contains_known_version_number_WHEN_load_THEN_version_number_returned_and_not_written(self):
        expected_version = self.first_version
        self.file_access.open_file = Mock(return_value=[expected_version])

        result = self.upgrade().get_version_number()

        assert_that(result, is_(expected_version), "Version number")
        assert_that(self.file_access.wrote_version, none())

    def test_GIVEN_config_contains_unknown_version_number_WHEN_upgrade_THEN_error(self):

        unknown_version = "unknown"
        self.file_access.open_file = Mock(return_value=[unknown_version])

        result = self.upgrade().upgrade()

        assert_that(result, is_not(0), "Success")
        assert_that(self.logger.log_err, contains_exactly("Unknown version number {0}".format(unknown_version)))

    def test_GIVEN_config_contains_latest_version_number_WHEN_load_THEN_program_exits_successfully(self):
        expected_version = "3.3.0"
        self.file_access.open_file = Mock(return_value=[expected_version])
        upgrade_steps = [(expected_version, None)]

        result = self.upgrade(upgrade_steps).upgrade()

        assert_that(result, is_(0), "Success exit")
        assert_that(self.logger.log, has_item("Current config is on latest version, no upgrade needed"))

    def test_GIVEN_config_contains_older_version_number_WHEN_upgrade_THEN_upgrade_done_and_program_exits_successfully(self):
        original_version = "3.2.1"
        final_version = "3.2.3"

        self.file_access.open_file = Mock(return_value=[original_version])
        upgrade_step = Mock(UpgradeStep)
        upgrade_step.perform = Mock(return_value=0)

        upgrade_steps = [(original_version, upgrade_step),
                         (final_version, None)]

        result = self.upgrade(upgrade_steps).upgrade()

        assert_that(result, is_(0), "Success exit")
        upgrade_step.perform.assert_called_once()
        assert_that(self.logger.log, has_item("Finished upgrade. Now on version {0}".format(final_version)))
        assert_that(self.file_access.wrote_version, is_(final_version), "Version written to file at the end")

    def test_GIVEN_config_contains_older_version_number_but_not_earliest_and_multiple_steps_WHEN_upgrade_THEN_all_upgrade_steps_equal_to_or_later_than_current_steps_are_done(self):
        original_version = "3.2.1"
        final_version = "3.2.3"

        self.file_access.open_file = Mock(return_value=[original_version])
        upgrade_step_no_to_do = Mock(UpgradeStep)
        upgrade_step_no_to_do.perform = Mock(return_value=0)
        upgrade_step_to_do_1 = Mock(UpgradeStep)
        upgrade_step_to_do_1.perform = Mock(return_value=0)
        upgrade_step_to_do_2 = Mock(UpgradeStep)
        upgrade_step_to_do_2.perform = Mock(return_value=0)
        upgrade_step_to_do_3 = Mock(UpgradeStep)
        upgrade_step_to_do_3.perform = Mock(return_value=0)

        upgrade_steps = [
            ("1.1.1", upgrade_step_no_to_do),
            ("1.1.2", upgrade_step_no_to_do),
            ("1.1.3", upgrade_step_no_to_do),
            (original_version, upgrade_step_to_do_1),
            (original_version, upgrade_step_to_do_2),
            (original_version, upgrade_step_to_do_3),
            (final_version, None)]

        result = self.upgrade(upgrade_steps).upgrade()

        assert_that(result, is_(0), "Success exit")
        upgrade_step_no_to_do.perform.assert_not_called()
        upgrade_step_to_do_1.perform.assert_called_once()
        upgrade_step_to_do_2.perform.assert_called_once()
        upgrade_step_to_do_3.perform.assert_called_once()
        assert_that(self.logger.log, has_item("Finished upgrade. Now on version {0}".format(final_version)))

    def test_GIVEN_empty_upgrade_steps_WHEN_init_THEN_error(self):
        try:
            Upgrade(None, None, [])
            raise AssertionError("Expecting UpgradeError got nothing")
        except UpgradeError:
            pass

    def test_GIVEN_no_final_version_in_upgrade_steps_WHEN_init_THEN_error(self):
        try:
            Upgrade(None, None, [("blah", Mock(UpgradeStep))])
            raise AssertionError("Expecting UpgradeError got nothing")
        except UpgradeError:
            pass

    def test_GIVEN_upgrade_step_failes_WHEN_upgrade_THEN_fail(self):
        original_version = "3.2.1"
        final_version = "3.2.3"
        expect_error_code = 1

        self.file_access.open_file = Mock(return_value=[original_version, ""])
        upgrade_step = Mock(UpgradeStep)
        upgrade_step.perform = Mock(return_value=expect_error_code)

        upgrade_steps = [(original_version, upgrade_step),
                         (final_version, None)]

        result = self.upgrade(upgrade_steps).upgrade()

        assert_that(result, is_(expect_error_code), "Fail exit")


if __name__ == '__main__':
    unittest.main()
