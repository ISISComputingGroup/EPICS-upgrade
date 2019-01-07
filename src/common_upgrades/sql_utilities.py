"""
Helpful sql utilities
"""
from getpass import getpass

import mysql.connector


class SqlConnection:
    """
    Class to allow sql access. Should be used in the top scope and sessions are got using get_session.
    """

    _connection = None

    def __init__(self):
        pass

    @staticmethod
    def get_session(logger):
        """
        Get the database session; creates one if needed.
        Args:
            logger: the logger to use

        Returns:
            sql connection
        """
        while SqlConnection._connection is None:
            try:
                root_pass = getpass("Please enter db root password: ")
                SqlConnection._connection = mysql.connector.connect(user='root', password=root_pass)
            except Exception as e:
                logger.error("Failed to connect to database: {}".format(e))
        return SqlConnection._connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close connection if this class created it
        if SqlConnection._connection is not None:
            SqlConnection._connection.close()


def run_sql(logger, sql):
    """
    Sends an SQL statement to the database.
    Args:
        logger: the logger to use to log messages
        sql: The statement to send
    """
    cursor = SqlConnection.get_session(logger).cursor()

    cursor.execute(sql)

    SqlConnection.get_session(logger).commit()
    cursor.close()


def add_new_user(logger, user, password):
    """
    Adds a user with all permissions to the exp_user database
    Args:
        logger: the logger to use to log messages
        user: The name of the user
        password: The password that the user will be required to use
    """
    try:
        run_sql(logger, "GRANT INSERT, SELECT, UPDATE, DELETE ON exp_data.* TO {} IDENTIFIED BY '{}';".format(
            user, password))
        return 0
    except Exception as e:
        logger.error("Failed to add user: {}".format(e))
        return -1
