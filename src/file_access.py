import os
from xml.dom import minidom
import shutil
from xml.parsers.expat import ExpatError
from src.common_upgrades.utils.constants import CONFIG_FOLDER, COMPONENT_FOLDER, SYNOPTIC_FOLDER


class FileAccess(object):
    """
    File access for the configuration
    """

    def __init__(self, logger, config_root):
        """
        Constructor

        Args:
            logger: the logger to use
            config_root: the root dir for the config (all files a relative to this directory).
                        Should normally be the parent of ICPCONFIGROOT.
        """
        self.config_base = config_root
        self._logger = logger

    def open_file(self, filename):
        """

        Open a file and return the object

        Args:
            filename: filename to open

        Returns:
            contents of file as a list of lines
        """
        with open(os.path.join(self.config_base, filename)) as f:
            lines = []
            for line in f:
                lines.append(line.rstrip())
        return lines

    def write_version_number(self, version, filename):
        """
        Write the version number to the file
        Args:
            version: version to write
            filename: filename to write to (relative to config root)

        Returns:

        """
        with open(os.path.join(self.config_base, filename), mode="w") as f:
            self._logger.info("Writing new version number {0}".format(version))
            f.write("{}\n".format(version))

    def write_file(self, filename, file_contents):
        """
        Write file contents (will overwrite existing files)

        Args:
            filename: filename to write to
            file_contents: the file contents to write as a list of strings (no new lines needed)

        Returns:

        """
        with open(os.path.join(self.config_base, filename), mode="w") as f:
            self._logger.info("Writing file {0}".format(filename))
            for line in file_contents:
                f.write("{}\n".format(line))

    def open_xml_file(self, filename):
        """
        Open a file and returns the xml it contains

        Args:
            filename: filename to open

        Returns:
            contents of file as an xml tree
        """
        return minidom.parse(os.path.join(self.config_base, filename))

    def write_xml_file(self, filename, xml):
        """

        Saves xml to a file

        Args:
            filename: filename to save
            xml: xml to save

        Returns:
        """

        # this can not use pretty print because that will cause it to gain tabs and newlines
        with open(os.path.join(self.config_base, filename), mode="w") as f:
            self._logger.info("Writing xml file {0}".format(filename))
            f.write('<?xml version="1.0" ?>\n')
            xml.firstChild.writexml(f)
            f.write('\n')

    def listdir(self, dir):
        """
        Returns a list of files in a directory
        
        Args:
            dir (String): The directory to list
            
        Return:
            List of file paths (strings)
        """
        return [os.path.join(dir, f) for f in os.listdir(os.path.join(self.config_base, dir))]

    def remove_file(self, filename):
        """
        Removes a file from the file system.

        Args:
            filename (str): The file to remove, relative to the config directory
        """
        self._logger.info("Removing file {}".format(filename))
        os.remove(os.path.join(self.config_base, filename))

    def delete_folder(self, path):
        """
        Deletes a folder recursively.

        Args:
            path (String): The folder to remove
        """
        shutil.rmtree(path)

    def is_dir(self, path):
        """
        Checks whether a path is a directory or file.

        Args:
            path (str): The path relative to the configuration directory.

        Returns:
            True if is a directory, false otherwise.
        """
        return os.path.isdir(os.path.join(self.config_base, path))

    def exists(self, path):
        return os.path.exists(os.path.join(self.config_base, path))

    def get_config_files(self, file_type):
        """
        Generator giving all the config files of a given type.

        Args:
            file_type: The type of file that you want to get e.g. iocs.xml

        Yields:
            Tuple: The path to the ioc file and its xml representation.
        """
        for path in [COMPONENT_FOLDER, CONFIG_FOLDER]:
            for config in [c for c in self.listdir(path) if self.is_dir(c)]:
                xml_path = os.path.join(config, file_type)
                try:
                    yield (xml_path, self.open_xml_file(xml_path))
                except IOError:
                    raise IOError("Cannot find {}".format(xml_path))
                except ExpatError as ex:
                    raise ExpatError("{} is invalid xml '{}'".format(path, ex))
