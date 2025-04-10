from abc import ABCMeta, abstractmethod


class UpgradeStep(object):
    """An upgrade step base object to be inherited from"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def perform(self, file_access, logger):  # noqa
        """Perform the upgrade step this should be implemented

        Args:
            file_access (FileAccess): file access
            logger (LocalLogger): logger

        Returns: exit code 0 success; anything else fail

        """
        raise NotImplementedError
