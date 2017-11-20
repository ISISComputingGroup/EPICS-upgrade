import unittest
from hamcrest import *
from mock import MagicMock as Mock

from src.upgrade_step_from_4p1p0 import UpgradeStepFrom4p1p0
from test import mother
from mother import LoggingStub, FileAccessStub


class TestUpgradeStepFrom4p1p0(unittest.TestCase):

    def setUp(self):
        self.file_access = FileAccessStub()
        self.upgrade_step = UpgradeStepFrom4p1p0()
        self.logger = LoggingStub()


if __name__ == '__main__':
    unittest.main()
