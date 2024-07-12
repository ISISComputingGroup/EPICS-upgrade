"""
Helpful sql utilities
"""

from getpass import getpass
import os
import re
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
                root_pass = os.getenv("MYSQL_PASSWORD") or getpass(
                    "Please enter db root password: "
                )
                SqlConnection._connection = mysql.connector.connect(user="root", password=root_pass)
            except Exception as e:
                logger.error("Failed to connect to database: {}".format(e))
        return SqlConnection._connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close connection if this class created it
        if SqlConnection._connection is not None:
            SqlConnection._connection.close()
            SqlConnection._connection = None


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


def run_sql_list(logger, sql_list):
    """
    Sends a list of SQL statement to the database.
    Args:
        logger: the logger to use to log messages
        sql_list: The statement to send
    """
    cursor = SqlConnection.get_session(logger).cursor()

    for sql in sql_list:
        for result in cursor.execute(sql, multi=True):
            pass

    SqlConnection.get_session(logger).commit()
    cursor.close()


def run_sql_file(logger, file):
    """
    Sends an SQL statement to the database.
    Args:
        logger: the logger to use to log messages
        file: The file of sql statement to send
    """
    if not os.path.exists(file):
        logger.error(f"Failed to open {file}")
        return -1
    statement_list = []
    lines = []
    with open(file) as f:
        lines = f.readlines()
    statement = ""
    for line in lines:
        if re.match(r"--", line) or re.match(r"#", line):
            continue
        statement = statement + line
        if re.search(r";[ ]*$", line):
            statement_list.append(statement)
            statement = ""

    logger.info(f"Applying DB schema from {file}")
    run_sql_list(logger, statement_list)
    return 0


def add_new_user(logger, user, password):
    """
    Adds a user with all permissions to the exp_user database
    Args:
        logger: the logger to use to log messages
        user: The name of the user in form 'username'@'host'
        password: The password that the user will be required to use
    """
    try:
        run_sql(
            logger,
            "CREATE USER {} IDENTIFIED WITH mysql_native_password BY '{}';".format(user, password),
        )
        run_sql(logger, "GRANT INSERT, SELECT, UPDATE, DELETE ON exp_data.* TO {};".format(user))
        return 0
    except Exception as e:
        logger.error("Failed to add user: {}".format(e))
        return -1
