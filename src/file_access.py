import os
from xml.dom import minidom
import shutil
from xml.parsers.expat import ExpatError
import six
from src.common_upgrades.utils.constants import CONFIG_FOLDER, COMPONENT_FOLDER, SYNOPTIC_FOLDER, \
    DEVICE_SCREEN_FILE, DEVICE_SCREENS_FOLDER


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
    
    def rename_file(self, filename, new_name):
        """
        
        Rename a file
        
        Args:
            filename: current filename
            new_name: new filename to rename to
        
        """
        os.rename(filename, new_name)

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

    def write_file(self, filename, file_contents, mode = "w", file_full=False):
        """
        Write file contents (will overwrite existing files)

        Args:
            filename: filename to write to
            file_contents: the file contents to write as a list of strings (no new lines needed)
            file_full: if true then file_contents should be a list of strings (no new lines needed),
            if false then it should be a string to be written directly

        Returns:

        """
        with open(os.path.join(self.config_base, filename), mode=mode) as f:
            self._logger.info("Writing file {0}".format(filename))
            if not file_full:
                for line in file_contents:
                    f.write("{}\n".format(line))
            else:
                f.write(file_contents)

    def create_directories(self, path):
        """
        Create directories starting at config base path

        Args:
            path: path for directories to be created

        Returns:

        """
        os.makedirs(os.path.dirname(os.path.join(self.config_base, path)), exist_ok=True)

    def line_exists(self, filename, string):
        """
        Check if string exists as a line in file
        """
        with open(os.path.join(self.config_base, filename), "r") as f:
            for line in f:
                if line == string:
                    return True
        return False

    def file_contains(self, filename, string):
        """
        Check if a string exists in a file
        """
        with open(os.path.join(self.config_base, filename), "r") as f:
            for line in f:
                if string in line:
                    return True
        return False

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

    def _get_xml(self, path):
        try:
            return self.open_xml_file(path)
        except IOError:
            raise IOError("Cannot find {}".format(path))
        except ExpatError as ex:
            raise ExpatError("{} is invalid xml '{}'".format(path, ex))

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
                yield xml_path, self._get_xml(xml_path)

    def get_synoptic_files(self):
        """
        Generator giving all the synoptic config files

        Yields:
            Tuple: The path to the synoptic file and its xml representation.
        """
        for synoptic_path in [filename for filename in self.listdir(SYNOPTIC_FOLDER) if filename.endswith('.xml')]:
            yield synoptic_path, self._get_xml(synoptic_path)

    def get_device_screens(self):
        """
        Returns the device screen file if it exists, else None.
        """
        device_screens_path = os.path.join(DEVICE_SCREENS_FOLDER, DEVICE_SCREEN_FILE)
        if os.path.exists(device_screens_path):
            return device_screens_path, self._get_xml(device_screens_path)
        else:
            return None

    def get_file_paths(self, directory: str, extension: str = None):
        """
        Generator giving the paths of all files inside a directory, recursively searching all subdirectories.

        Args:
            directory: The directory to search.
            extension: Optional file extension to filter by.

        Yields:
            str: The path to the file.
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if extension is None or file.endswith(extension):
                    yield os.path.join(root, file)


class CachingFileAccess(object):
    """
    Context that uses the given file access object but does not actually write to file until the context is left
    without an error.
    """
    def __init__(self, file_access):
        self.cached_writes = dict()
        self._file_access = file_access

    def __enter__(self):
        self.old_write_method = self._file_access.write_xml_file
        self.old_open_method = self._file_access.open_xml_file
        self._file_access.write_xml_file = self.write_xml_file
        self._file_access.open_xml_file = self.open_xml_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file_access.write_xml_file = self.old_write_method
        self._file_access.open_xml_file = self.old_open_method
        if exc_type is None:
            self.write()

    def open_xml_file(self, filename):
        """
        Open a file and returns the xml it contains (returns the cached file if it exists)

        Args:
            filename: filename to open

        Returns:
            contents of file as an xml tree
        """
        if filename in six.iterkeys(self.cached_writes):
            return self.cached_writes[filename]
        else:
            return self.old_open_method(filename)

    def write_xml_file(self, filename, xml):
        """
        Caches a write of xml to a file

        Args:
            filename: filename to save
            xml: xml to save
        """
        self.cached_writes[filename] = xml

    def write(self):
        """
        Write all cached writes to the file.
        """
        for filename, xml in six.iteritems(self.cached_writes):
            self._file_access.write_xml_file(filename, xml)
