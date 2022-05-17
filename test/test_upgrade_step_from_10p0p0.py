import os
import unittest
from mother import LoggingStub, FileAccessStub
from src.file_access import FileAccess
from src.upgrade_step_from_10p0p0 import RemoveReflDeviceScreen

CONFIG_ROOT = os.path.abspath(os.path.join("config-test"))
SCREEN_FILE_PATH = os.path.join("configurations", "devices", "screens.xml")

SCREENS_FILE = """<?xml version="1.0" ?>
<devices xmlns="http://epics.isis.rl.ac.uk/schema/screens/1.0/">
	<device>
		<name>Screen</name>
		<key>PEARLPC</key>
		<type>OPI</type>
		<properties>
			<property>
				<key>PEARLPC</key>
				<value>PEARLPC_01</value>
			</property>
		</properties>
	</device>
	<device>
		<name>Screen_1</name>
		<key>Tektronix AFG3000</key>
		<type>OPI</type>
		<properties>
			<property>
				<key>TEKAFG3XXX</key>
				<value>TEKAFG3XXX_01</value>
			</property>
		</properties>
	</device>
	<device>
		<name>Screen_2</name>
		<key>Reflectometry OPI</key>
		<type>OPI</type>
		<properties/>
	</device>
</devices>
"""


class TestRemoveReflDeviceScreen(unittest.TestCase):

    def setUp(self):
        self.upgrade_step = RemoveReflDeviceScreen()
        self.logger = LoggingStub()
        self.file_access = FileAccess(self.logger, CONFIG_ROOT)

    def test_GIVEN_refl_device_screen_in_config_WHEN_upgrade_performed_THEN_screen_removed(self):
        # Given
        self.file_access.create_directories(SCREEN_FILE_PATH)
        self.file_access.write_file(SCREEN_FILE_PATH, SCREENS_FILE, file_full=True)
        self.assertTrue(self.file_access.file_contains(SCREEN_FILE_PATH, "<key>Reflectometry OPI</key>"))
        self.assertTrue(self.file_access.exists(SCREEN_FILE_PATH))
        # When
        self.upgrade_step.perform(self.file_access, self.logger)
        # Then
        self.assertFalse(self.file_access.file_contains(SCREEN_FILE_PATH, "<key>Reflectometry OPI</key>"))

        # Cleanup created files
        self.file_access.remove_file(os.path.join(CONFIG_ROOT, SCREEN_FILE_PATH))
        self.file_access.delete_folder(CONFIG_ROOT)
        self.assertFalse(self.file_access.exists(SCREEN_FILE_PATH))

    def test_GIVEN_no_device_screen_in_config_THEN_nothing_happens_without_errors(self):
        # Given
        if self.file_access.exists(SCREEN_FILE_PATH):
            self.file_access.remove_file(os.path.join(CONFIG_ROOT, SCREEN_FILE_PATH))
            self.file_access.delete_folder(CONFIG_ROOT)
        self.assertFalse(self.file_access.exists(SCREEN_FILE_PATH))
        # Then
        self.upgrade_step.perform(self.file_access, self.logger)


if __name__ == '__main__':
    unittest.main()
