import mysql.connector

from src.upgrade_step import UpgradeStep


class UpgradeStepFrom5p0p1(UpgradeStep):
    """
    Add a new user who can write to the exp database.
    """

    def perform(self, file_access, logger):
        """
        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail
        """
        self.logger = logger
        try:
            root_pass = raw_input("Please enter db root password: ")
            self.connection = mysql.connector.connect(user='root', password=root_pass)
        except Exception as e:
            self.logger.error("Failed to connect to database: {}".format(e))
            return -1

        ret = self.add_new_user('exp_data_writer@130.246.39.152', '$exp_data_writer')
        ret += self.add_new_user('exp_data_writer@130.246.54.107', '$exp_data_writer')
        ret += self.flush_privileges()
        return ret

    def write_sql(self, sql):
        """
        Sends an SQL statement to the database.
        Args:
            sql: The statement to send
        """
        cursor = self.connection.cursor()

        cursor.execute(sql)

        self.connection.commit()
        cursor.close()


    def flush_privileges(self):
        """
        Flushes new privileges to the database.
        """
        try:
            self.write_sql("FLUSH PRIVILEGES;")
            return 0
        except Exception as e:
            self.logger.error("Failed to flush privileges: {}".format(e) )
            return -1

    def add_new_user(self, user, password):
        """
        Adds a user with all permissions to the exp_user database
        Args:
            user: The name of the user
            password: The password that the user will be required to use
        """
        try:
            self.write_sql("GRANT INSERT, SELECT, UPDATE, DELETE ON exp_data.* TO {} IDENTIFIED BY '{}';"
                           .format(user, password))
            return 0
        except Exception as e:
            self.logger.error("Failed to add user: {}".format(e) )
            return -1
