import os

from src.upgrade_step import UpgradeStep


class UpgradeStepFrom4p3p1(UpgradeStep):

    def perform(self, file_access, logger):
        """
        Perform the upgrade step from version 0 to 1

        Returns: exit code 0 success; anything else fail
        """
        filename = os.path.join("configurations", "banner.xml")
        file_contents = ["""<?xml version="1.0" ?>
<banner xmlns="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:blk="http://epics.isis.rl.ac.uk/schema/banner/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
<items>
 <item>
  <name>DAE Simulation mode</name>
  <pv>DAE:SIM_MODE</pv>
  <local>true</local>
 </item>
 <item>
  <name>Manager mode</name>
  <pv>CS:MANAGER</pv>
  <local>true</local>
 </item>
 </items>
</banner>
"""]

        file_access.write_file(filename, file_contents)
        return 0
