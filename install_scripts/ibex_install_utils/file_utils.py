"""
Filesystem utility classes
"""

import os
import shutil
import stat
from time import sleep

from ibex_install_utils.exceptions import ErrorWithFile


class FileUtils(object):
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def delete_if_exists(path):
        """
        Delete a file path if it exists
        Args:
            path: path to delete

        Returns:

        Raises ErrorWithFile: if it can not delete a file

        """
        def on_error_make_read_write(func, current_path, exc_info):
            """
            If there is an error then make file read write and try again
            Args:
                func: function it was in
                current_path: path it had troubles with
                exc_info: exception information

            Returns:

            """
            if exc_info[0] is WindowsError:
                try:
                    try:
                        # try remove second time (doesn't always work first time)
                        if func == os.rmdir:
                            sleep(0.1)
                            os.rmdir(current_path)
                            return
                    except WindowsError:
                        pass

                    os.chmod(current_path, stat.S_IRWXU)
                    os.remove(current_path)
                    return
                except Exception:
                    pass
            raise ErrorWithFile(
                "Failed to delete file {file} from epics because: {error}".format(file=current_path,
                                                                                  error=str(exc_info)))

        if os.path.isdir(path):
            shutil.rmtree(path, onerror=on_error_make_read_write)

    def mkdir_recursive(self, path):
        """
        Make a directory and all its ancestors
        Args:
            path: path of directory

        Returns:

        """
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self.mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def remove_dir(path):
        """
        Remove a directory, even if non-empty

        Args:
            path: Directory to delete
        """
        def onerror(func, path, exc_info):
            """
            Error handler for ``shutil.rmtree``.

            If the error is due to an access error (read only file)
            it attempts to add write permission and then retries.

            If the error is for another reason it re-raises the error.

            :param func: Action taken on the path
            :param path: Path that is being manipulated
            :param exc_info: Whether to log execution info
            """
            if not os.access(path, os.W_OK):  # Is the error an access error ?
                os.chmod(path, stat.S_IWUSR)
                func(path)
            elif exc_info:
                raise OSError("Unable to delete file at {}".format(path))

        shutil.rmtree(path, onerror=onerror)

    @staticmethod
    def move_dir(src, dst):
        """
        Moves a dir. Better to copy remove so we can handle permissions issues

        Args:
            src: Source directory
            dst: Destination directory
        """
        shutil.copytree(src, dst)
        FileUtils.remove_dir(src)