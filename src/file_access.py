import os
from xml.dom import minidom


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
        self._config_base = config_root
        self._logger = logger

    def open_file(self, filename):
        """

        Open a file and return the object

        Args:
            filename: filename to open

        Returns:
            contents of file as a list of lines
        """
        with file(os.path.join(self._config_base, filename)) as f:
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
        with file(os.path.join(self._config_base, filename), mode="w") as f:
            self._logger.info("Writing new version number {0}".format(version))
            f.write("{0}{1}".format(version, os.linesep))

    def write_file(self, filename, file_contents):
        """
        Write file contents (will overwrite existing files)

        Args:
            filename: filename to write to
            file_contents: the file contents to write as a list of strings (no new lines neeeded)

        Returns:

        """
        with file(os.path.join(self._config_base, filename), mode="w") as f:
            self._logger.info("Writing file {0}".format(filename))
            for line in file_contents:
                f.write("{0}{1}".format(line, os.linesep))

    def open_xml_file(self, filename):
        """

        Open a file and returns the xml it contains

        Args:
            filename: filename to open

        Returns:
            contents of file as an xml tree
        """
        return minidom.parse(os.path.join(self._config_base, filename))

    def write_xml_file(self, filename, xml):
        """

        Saves xml to a file

        Args:
            filename: filename to save
            xml: xml to save

        Returns:
        """

        # this can not use pretty print because that will cause it to gain tabs and newlines
        with file(os.path.join(self._config_base, filename), mode="w") as f:
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
        return [os.path.join(dir, f) for f in os.listdir(os.path.join(self._config_base, dir))]
