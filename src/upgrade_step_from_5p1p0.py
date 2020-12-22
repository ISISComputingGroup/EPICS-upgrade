import os

from src.upgrade_step import UpgradeStep

from win32serviceutil import StopService, QueryServiceStatus, RemoveService
import pywintypes
from time import sleep


class RemoveOldExpPopulator(UpgradeStep):
    """
    Step that removes the old experiment populator that is running as a service
    """
    WAIT_FOR_STOPPED_TIME = 10

    RB_service_name = "RBService"
    RB_program_location = os.path.join(os.path.sep, "Program Files (x86)", "STFC ISIS Facility", "RB Number Finder")

    def perform(self, file_access, logger):
        self.logger = logger
        try:
            self.stop_and_remove_service(self.RB_service_name)
            self.delete_populator(file_access)
            return 0
        except Exception as e:
            return -1

    def delete_populator(self, file_access):
        FOLDER_NOT_FOUND = 3
        PATH_NOT_FOUND = 2
        try:
            file_access.delete_folder(self.RB_program_location)
        except Exception as e:
            if isinstance(e, OSError) and (e.errno == FOLDER_NOT_FOUND or e.errno == PATH_NOT_FOUND):
                self.logger.info("RB populator not installed, no need to uninstall")
            else:
                self.logger.error("Failed to remove RB populator: {}".format(e))
                raise

    def stop_and_remove_service(self, service_name):
        # Service status codes from
        # https://docs.microsoft.com/en-gb/windows/desktop/api/winsvc/ns-winsvc-_service_status
        SERVICE_RUNNING = 4
        SERVICE_STOPPED = 1
        # Error code from https://msdn.microsoft.com/en-us/library/ms932980.aspx
        SERVICE_DOES_NOT_EXIST = 1060

        try:
            service_status = QueryServiceStatus(service_name)
        except Exception as e:
            if isinstance(e, pywintypes.error) and e.args[0] == SERVICE_DOES_NOT_EXIST:
                self.logger.info("RB populator service not installed, no need to uninstall")
                return
            else:
                self.logger.error("Failed to find service: {} (service may still exist)".format(e))
                raise

        if service_status[1] == SERVICE_RUNNING:
            try:
                StopService(service_name)
                self.logger.info("Waiting for service to stop")
                for i in range(self.WAIT_FOR_STOPPED_TIME):
                    if QueryServiceStatus(service_name)[1] == SERVICE_STOPPED:
                        break
                    elif i == self.WAIT_FOR_STOPPED_TIME-1:
                        raise Exception("Could not stop after {} seconds".format(self.WAIT_FOR_STOPPED_TIME))
                    sleep(1)
            except Exception as e:
                self.logger.error("Unable to stop service: {}".format(e))
                raise

        try:
            RemoveService(service_name)
        except Exception as e:
            self.logger.error("Unable to remove service: {}".format(e))
            raise
