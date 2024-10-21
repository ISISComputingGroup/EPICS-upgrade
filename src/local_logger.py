import datetime
import os
import sys


class LocalLogger(object):
    """A local logging object which will write to the screen and a file"""

    def __init__(self, log_dir):
        """The logging directory in to which to write the log file

        Args:
            log_dir: the directory for the file
        """
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        log_file = os.path.join(
            log_dir,
            "upgrade_{0}.txt".format(
                datetime.datetime.now().strftime("%Y_%m_%d__%H_%M")
            ),
        )

        self._log_file = log_file

    def error(self, message):
        """Write the message as an error (to standard err with ERROR in front of it)

        Args:
            message: message to write (no new lines needed)

        Returns:

        """
        formatted_message = "ERROR: {0}{1}".format(message, os.linesep)
        with open(self._log_file, mode="a") as f:
            f.write(formatted_message)
        sys.stderr.write(formatted_message)

    def info(self, message):
        """Write the message as info (to standard out with INFO in front of it)

        Args:
            message: message to write (no new lines needed)

        Returns:

        """
        formatted_message = " INFO: {0}{1}".format(message, os.linesep)
        with open(self._log_file, mode="a") as f:
            f.write(formatted_message)
        sys.stdout.write(formatted_message)
