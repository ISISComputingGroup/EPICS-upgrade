import unittest

import unittest.mock as mocked
import mysql.connector
from mock import MagicMock, patch

from src.common_upgrades.sql_utilities import SqlConnection, run_sql


class TestSQLUtils(unittest.TestCase):
    def setUp(self):
        SqlConnection._connection = None

    @patch("src.common_upgrades.sql_utilities.getpass")
    @patch(
        "src.common_upgrades.sql_utilities.mysql.connector", autospec=mysql.connector
    )
    def test_GIVEN_no_connection_WHEN_connection_created_THEN_no_password_prompted(
        self, mysql, getpass
    ):
        with SqlConnection():
            pass
        mysql.assert_not_called()
        getpass.assert_not_called()

    @patch("src.common_upgrades.sql_utilities.getpass")
    @patch(
        "src.common_upgrades.sql_utilities.mysql.connector", autospec=mysql.connector
    )
    def test_GIVEN_no_connection_WHEN_run_sql_called_THEN_password_prompted(
        self, mysql, getpass
    ):
        with SqlConnection():
            run_sql(MagicMock(), MagicMock())
        getpass.assert_called_once()
        mysql.connect.assert_called_once()

    @patch("src.common_upgrades.sql_utilities.getpass")
    @patch(
        "src.common_upgrades.sql_utilities.mysql.connector", autospec=mysql.connector
    )
    def test_GIVEN_a_pre_existing_connection_WHEN_run_sql_called_THEN_password_not_prompted(
        self, mysql, getpass
    ):
        with SqlConnection():
            run_sql(MagicMock(), MagicMock())

            getpass.reset_mock()
            mysql.reset_mock()

            run_sql(MagicMock(), MagicMock())

            getpass.assert_not_called()
            mysql.connect.assert_not_called()

    @patch("src.common_upgrades.sql_utilities.getpass")
    @patch(
        "src.common_upgrades.sql_utilities.mysql.connector", autospec=mysql.connector
    )
    def test_WHEN_run_sql_called_THEN_changes_committed_and_cursor_closed(
        self, mysql, getpass
    ):
        with SqlConnection():
            run_sql(MagicMock(), MagicMock())

            commit = mocked.create_autospec(
                SqlConnection.get_session(MagicMock()).commit
            )
            cursor = mocked.create_autospec(
                SqlConnection.get_session(MagicMock()).cursor()
            )
            commit.assert_called()
            cursor.assert_called()

    @patch("src.common_upgrades.sql_utilities.getpass")
    @patch(
        "src.common_upgrades.sql_utilities.mysql.connector", autospec=mysql.connector
    )
    def test_WHEN_run_sql_called_THEN_sql_executed(self, mysql, getpass):
        with SqlConnection():
            my_SQL_string = "TEST SQL"
            run_sql(MagicMock(), my_SQL_string)

            execute = mocked.create_autospec(
                SqlConnection.get_session(MagicMock()).cursor().execute
            )
            execute.assert_called_with(my_SQL_string)
