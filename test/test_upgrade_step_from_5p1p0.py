try:
    import pywintypes
    from src.upgrade_step_from_5p1p0 import RemoveOldExpPopulator
except ImportError as e:
    pywintypes = None

import unittest
from mock import patch, Mock

class TestUpgradeStepFrom5p0p1Changes(unittest.TestCase):

    def setUp(self):
        if not pywintypes:
            self.skipTest("Failed to import pywintypes and win32serviceutil, probably as this is windows specific.")
        self.upgrade_step = RemoveOldExpPopulator()
        self.upgrade_step.logger = Mock()

    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus')
    def test_GIVEN_service_does_not_exist_WHEN_stopping_service_THEN_no_error(self, query_patch):
        query_patch.side_effect = pywintypes.error(1060)

        self.upgrade_step.stop_and_remove_service("TEST")

        self.upgrade_step.logger.info.assert_called_once()

    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus')
    def test_GIVEN_service_query_fails_with_win_error_WHEN_stopping_service_THEN_error(self, query_patch):
        query_patch.side_effect = pywintypes.error(404)

        with self.assertRaises(pywintypes.error):
            self.upgrade_step.stop_and_remove_service("TEST")

    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus')
    def test_WHEN_query_service_fails_THEN_error(self, query_patch):
        query_patch.side_effect = Exception("An error")

        with self.assertRaises(Exception):
            self.upgrade_step.stop_and_remove_service("TEST")

    @patch('src.upgrade_step_from_5p1p0.RemoveService')
    @patch('src.upgrade_step_from_5p1p0.StopService')
    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus', return_value=[0, 1])
    def test_GIVEN_service_not_running_WHEN_service_removed_THEN_not_stopped(self, query, stop, remove):
        self.upgrade_step.stop_and_remove_service("TEST")

        self.assertFalse(stop.called)
        remove.assert_called_once()

    @patch('src.upgrade_step_from_5p1p0.RemoveService')
    @patch('src.upgrade_step_from_5p1p0.StopService')
    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus', return_value=[0, 4])
    def test_GIVEN_service_running_and_not_stopping_WHEN_service_removed_THEN_service_queried_repeatedly_and_exception_rasied(
            self, query, stop, remove):
        self.upgrade_step.WAIT_FOR_STOPPED_TIME = 2

        with self.assertRaises(Exception):
            self.upgrade_step.stop_and_remove_service("TEST")

        self.assertEqual(query.call_count, self.upgrade_step.WAIT_FOR_STOPPED_TIME+1)
        stop.assert_called_once()

    @patch('src.upgrade_step_from_5p1p0.RemoveService')
    @patch('src.upgrade_step_from_5p1p0.StopService', side_effect=IndexError())
    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus', return_value=[0, 4])
    def test_GIVEN_service_running_WHEN_service_stopped_failed_THEN_exception_raised(self, query, stop, remove):
        with self.assertRaises(IndexError):
            self.upgrade_step.stop_and_remove_service("TEST")

    @patch('src.upgrade_step_from_5p1p0.RemoveService')
    @patch('src.upgrade_step_from_5p1p0.StopService')
    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus', side_effect=[[0, 4], [0, 1]])
    def test_GIVEN_service_running_WHEN_service_stopped_THEN_service_remove_called(self, query, stop, remove):
        self.upgrade_step.stop_and_remove_service("TEST")

        remove.assert_called_once()

    @patch('src.upgrade_step_from_5p1p0.RemoveService', side_effect=Exception())
    @patch('src.upgrade_step_from_5p1p0.StopService')
    @patch('src.upgrade_step_from_5p1p0.QueryServiceStatus', side_effect=[[0, 4], [0, 1]])
    def test_GIVEN_remove_service_failing_WHEN_service_removed_THEN_exception_raised(self, query, stop, remove):
        with self.assertRaises(Exception):
            self.upgrade_step.stop_and_remove_service("TEST")

    def test_GIVEN_delete_successful_WHEN_populator_removed_THEN_no_error(self):
        file_access = Mock()
        self.upgrade_step.delete_populator(file_access)

        file_access.delete_folder.assert_called_once()

    def test_GIVEN_file_not_found_WHEN_populator_removed_THEN_no_error(self):
        file_access = Mock()
        exception = OSError()
        exception.errno = 3
        file_access.delete_folder.side_effect = exception

        self.upgrade_step.delete_populator(file_access)

        file_access.delete_folder.assert_called_once()
        self.upgrade_step.logger.info.assert_called_once()

    def test_GIVEN_remove_failed_WHEN_populator_removed_THEN_exception_rasied(self):
        file_access = Mock()
        file_access.delete_folder.side_effect = Exception()

        with self.assertRaises(Exception):
            self.upgrade_step.delete_populator(file_access)


if __name__ == '__main__':
    unittest.main()
