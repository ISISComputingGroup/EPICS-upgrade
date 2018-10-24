import unittest
from src.upgrade_step_from_5p0p1 import UpgradeMotionSetpoints


class TestUpgradeMotionSetpointsChanges(unittest.TestCase):

    def setUp(self):
        self.upgrade_step = UpgradeMotionSetpoints()

    def test_GIVEN_blank_input_file_WHEN_adding_inpos_db_THEN_do_nothing(self):
        expected = [""]
        file_content = [""]

        self.upgrade_step.append_load_inpos_instructions(file_content)

        self.assertListEqual(expected, file_content)

    def test_GIVEN_input_file_with_unrelated_lines_WHEN_modifying_content_THEN_no_lines_added(self):
        file_content = ["some", "other", "lines"]
        expected = len(file_content)

        self.upgrade_step.append_load_inpos_instructions(file_content)

        self.assertEquals(expected, len(file_content))

    def test_GIVEN_input_file_with_dbloadrecord_lines_WHEN_modifying_content_THEN_equivalent_amount_of_lines_added(self):
        file_content = ["some", UpgradeMotionSetpoints.LOAD_MOTION_SP_DB_INSTRUCTION + "1", "other", UpgradeMotionSetpoints.LOAD_MOTION_SP_DB_INSTRUCTION + "2", "lines"]
        expected = len(file_content) + 2

        self.upgrade_step.append_load_inpos_instructions(file_content)

        self.assertEquals(expected, len(file_content))

    def test_GIVEN_input_file_with_dbloadrecords_with_all_macros_set_WHEN_adding_inpos_db_THEN_dbloadrecordsloop_instruction_added_with_macros(self):
        TEST_PREFIX = "TEST_PREFIX"
        TEST_NAME = "TEST_NAME"
        TEST_AXIS = "TEST_AXIS"
        TEST_TOLERANCE = 0.1
        TEST_LKUP = "TEST_LKUP"
        setpoint_instruction = UpgradeMotionSetpoints.LOAD_MOTION_SP_DB_INSTRUCTION
        inpos_instruction = UpgradeMotionSetpoints.LOAD_INPOS_DB_INSTRUCTION
        inpos_loop_suffix = '"NUMPOS", 0, 30)'
        macros = '"P={pref},NAME1={name},AXIS1={axis},TOL={tol},LOOKUP={lkup}")'.format(
                pref=TEST_PREFIX, name=TEST_NAME, axis=TEST_AXIS, tol=TEST_TOLERANCE, lkup=TEST_LKUP)
        dbload_instruction = setpoint_instruction + "," + macros + ")"
        file_content = [dbload_instruction]

        self.upgrade_step.append_load_inpos_instructions(file_content)

        expected = inpos_instruction + "," + macros + "," + inpos_loop_suffix
        self.assertEquals(expected, file_content[1])


if __name__ == '__main__':
    unittest.main()
