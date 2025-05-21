import unittest

from src.common_upgrades import change_pv_in_dashboard
from test.mother import FileAccessStub, LoggingStub

test_db = [
    'record(stringin, "$(P)CS:DASHBOARD:BANNER:LEFT:LABEL") {\n',
    " # starting comment\n",
    '    field(VAL, "Run:") # inline comment\n',
    '    field(PINI, "YES")\n',
    '    info(archive, "VAL")\n',
    "}\n",
    "\n",
    'record(scalcout, "$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL") {\n',
    '    field(INPA, "$(P)DAE:SIM_MODE CP MS")\n',
    '    field(BB, "DAE")\n',
    '    field(CC, "")\n',
    '    field(CALC, "A==1?BB:CC")\n',
    "    # Multiline\n",
    "    # x2\n",
    "}\n",
    "\n",
    "# comment before a record\n",
    'record(stringin, "$(P)CS:DASHBOARD:TAB:1:1:LABEL") {\n',
    "# blah\n",
    '    field(VAL, "Good / Raw Frames:")\n',
    '    field(PINI, "YES")\n',
    '    info(archive, "VAL")\n',
    "}\n",
    "# comment after a record\n",
]


class TestChangePVInDashboard(unittest.TestCase):
    def setUp(self):
        self.file_access = FileAccessStub()
        self.logger = LoggingStub()
        self.reader = change_pv_in_dashboard.ChangePvInDashboard(self.file_access, self.logger)

    def test_GIVEN_record_starts_THEN_finds_end(self):
        dummy_file = ["", "", "", 'record(blah, "blah") {\n', "", "", "", "}"]
        self.assertEqual(change_pv_in_dashboard._get_end_of_record(dummy_file, 3), 7)

    def test_GIVEN_record_starts_and_no_end_THEN_returns_invalid(self):
        dummy_file = ["", "", "", 'record(blah, "blah") {\n', "", "", "", ""]
        self.assertEqual(change_pv_in_dashboard._get_end_of_record(dummy_file, 3), -1)

    def test_GIVEN_record_starts_end_commented_THEN_returns_invalid(self):
        dummy_file = ["", "", "", 'record(blah, "blah") {\n', "", "#}", "", ""]
        self.assertEqual(change_pv_in_dashboard._get_end_of_record(dummy_file, 3), -1)

    def test_GIVEN_record_starts_end_commented_using_macro_THEN_finds_end(self):
        dummy_file = [
            "",
            "",
            "",
            'record(blah, "blah") {\n',
            "",
            "$(MACROTEST=#)}",
            "",
            "",
        ]
        self.assertEqual(change_pv_in_dashboard._get_end_of_record(dummy_file, 3), 5)

    def test_GIVEN_record_exists_THEN_get_correct_record(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)

        self.assertEqual(record.start, 17)
        self.assertEqual(record.end, 22)
        self.assertEqual(record.startline, 'record(stringin, "$(P)CS:DASHBOARD:TAB:1:1:LABEL") {\n')
        self.assertEqual(record.name, "$(P)CS:DASHBOARD:TAB:1:1:LABEL")
        self.assertEqual(record.type, "stringin")
        self.assertEqual(record.fields["VAL"][0], "Good / Raw Frames:")
        self.assertEqual(record.fields["PINI"][0], "YES")
        self.assertEqual(record.info["archive"][0], "VAL")
        self.assertEqual(record.start_comment, ["# blah\n"])

    def test_GIVEN_record_does_not_exist_THEN_get_none(self):
        self.assertIsNone(self.reader.get_record("$(P)CS:FALSE:DB", test_db))

    def test_GIVEN_record_exists_THEN_getters_return_line_in_db(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:LEFT:LABEL", test_db)
        fields = record.get_fields()
        info = record.get_info()
        self.assertListEqual(fields, test_db[2:4])
        self.assertEqual(info[0], test_db[4])

    def test_GIVEN_record_exists_AND_multi_line_comment_THEN_getters_return_line_in_db(
        self,
    ):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", test_db)
        fields = record.get_fields()
        self.assertListEqual(fields, test_db[8:14])

    def test_GIVEN_record_exists_THEN_change_name_changes_name_AND_startline(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:LEFT:LABEL", test_db)
        record.change_name("DIFFERENT:NAME")
        self.assertEqual(record.name, "DIFFERENT:NAME")
        self.assertEqual(record.startline, 'record(stringin, "DIFFERENT:NAME") {\n')
        new_db = record.update_record(test_db)
        self.assertEqual(new_db, ['record(stringin, "DIFFERENT:NAME") {\n'] + test_db[1:])

    def test_GIVEN_record_exists_THEN_change_type_changes_type_AND_startline(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:LEFT:LABEL", test_db)
        record.change_type("stringout")
        self.assertEqual(record.type, "stringout")
        self.assertEqual(
            record.startline,
            'record(stringout, "$(P)CS:DASHBOARD:BANNER:LEFT:LABEL") {\n',
        )

    def test_GIVEN_record_exists_THEN_change_type_AND_name_changes_type_name_AND_startline(
        self,
    ):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:LEFT:LABEL", test_db)
        record.change_type("stringout")
        record.change_name("DIFFERENT:NAME")
        self.assertEqual(record.name, "DIFFERENT:NAME")
        self.assertEqual(record.type, "stringout")
        self.assertEqual(record.startline, 'record(stringout, "DIFFERENT:NAME") {\n')

    def test_GIVEN_change_fields_THEN_field_is_changed(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", test_db)
        record.change_field("BB", "Altered")

        self.assertEqual(record.fields["BB"][0], "Altered")
        self.assertEqual(record.fields["BB"][1], '    field(BB, "Altered")\n')

    def test_GIVEN_change_fields_and_add_comment_THEN_field_is_changed(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", test_db)
        record.change_field("BB", "Altered", "blah blah blah")

        self.assertEqual(record.fields["BB"][0], "Altered")
        self.assertEqual(record.fields["BB"][1], '    field(BB, "Altered") #blah blah blah\n')

    def test_GIVEN_change_info_THEN_info_is_changed(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.change_info("archive", "Altered", "new comment")

        self.assertEqual(record.info["archive"][0], "Altered")
        self.assertEqual(record.info["archive"][1], '    info(archive, "Altered") #new comment\n')

    def test_GIVEN_add_field_THEN_field_is_added(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.add_field("INDD", "$(P)DAE:DAETIMINGSOURCE CP MS", "new line")

        self.assertEqual(record.fields["INDD"][0], "$(P)DAE:DAETIMINGSOURCE CP MS")
        self.assertEqual(
            record.fields["INDD"][1],
            '    field(INDD, "$(P)DAE:DAETIMINGSOURCE CP MS") #new line\n',
        )

    def test_GIVEN_add_info_THEN_info_is_added(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", test_db)
        record.add_info("archive", "VAL")

        self.assertEqual(record.info["archive"][0], "VAL")
        self.assertEqual(record.info["archive"][1], '    info(archive, "VAL")\n')

    def test_GIVEN_add_field_WHEN_field_already_exists_THEN_no_change(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:BANNER:MIDDLE:_VCAL", test_db)
        record.add_field("BB", "Altered", "blah blah blah")

        self.assertNotEqual(record.fields["BB"][0], "Altered")
        self.assertNotEqual(record.fields["BB"][1], '    field(BB, "Altered") #blah blah blah\n')

    def test_GIVEN_add_info_WHEN_info_already_exists_THEN_no_change(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.add_info("archive", "Altered", "new comment")

        self.assertNotEqual(record.info["archive"][0], "Altered")
        self.assertNotEqual(
            record.info["archive"][1], '    info(archive, "Altered") #new comment\n'
        )

    def test_GIVEN_field_exists_THEN_delete_removes_it(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.delete_field("PINI")
        self.assertNotIn("PINI", record.fields.keys())

    def test_GIVEN_info_exists_THEN_delete_removes_it(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.delete_info("archive")
        self.assertNotIn("archive", record.info.keys())

    def test_GIVEN_field_not_exists_THEN_delete_no_change(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        original_length = len(record.fields)
        record.delete_field("blah")
        self.assertEqual(original_length, len(record.fields))

    def test_GIVEN_info_not_exists_THEN_delete_no_change(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        original_length = len(record.info)
        record.delete_info("no info")
        self.assertEqual(original_length, len(record.info))

    def test_GIVEN_only_change_functions_THEN_total_lines_unchanged(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.change_type("stringout")
        record.change_name("DIFFERENT:NAME")
        record.change_field("VAL", "Altered")
        record.change_info("archive", "Altered")

        output = record.update_record(test_db)
        self.assertEqual(len(output), len(test_db))
        self.assertEqual(
            output,
            test_db[:17]
            + [
                'record(stringout, "DIFFERENT:NAME") {\n',
                "# blah\n",
                '    field(VAL, "Altered")\n',
                '    field(PINI, "YES")\n',
                '    info(archive, "Altered")\n',
                "}\n",
                "# comment after a record\n",
            ],
        )

    def test_GIVEN_only_add_functions_THEN_total_lines_greater(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.add_field("EGU", "cm")
        record.add_info("alarm", "dashboard")

        output = record.update_record(test_db)
        self.assertGreater(len(output), len(test_db))
        self.assertEqual(
            output,
            test_db[:17]
            + [
                'record(stringin, "$(P)CS:DASHBOARD:TAB:1:1:LABEL") {\n',
                "# blah\n",
                '    field(VAL, "Good / Raw Frames:")\n',
                '    field(PINI, "YES")\n',
                '    field(EGU, "cm")\n',
                '    info(archive, "VAL")\n',
                '    info(alarm, "dashboard")\n',
                "}\n",
                "# comment after a record\n",
            ],
        )

    def test_GIVEN_only_delete_functions_THEN_total_lines_lesser(self):
        record = self.reader.get_record("$(P)CS:DASHBOARD:TAB:1:1:LABEL", test_db)
        record.delete_field("VAL")
        record.delete_info("archive")

        output = record.update_record(test_db)
        self.assertLess(len(output), len(test_db))
        self.assertEqual(
            output,
            test_db[:17]
            + [
                'record(stringin, "$(P)CS:DASHBOARD:TAB:1:1:LABEL") {\n',
                "# blah\n",
                '    field(PINI, "YES")\n',
                "}\n",
                "# comment after a record\n",
            ],
        )


if __name__ == "__main__":
    unittest.main()
