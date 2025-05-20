from src.common_upgrades.utils.constants import DASHBOARD_DB_FILENAME
import re
from typing import Optional


class Record:
    """
    Class to contain the information in a single db record.
    """

    def __init__(self, lines: list[str], start: int, end: int) -> None:
        self.type, self.name, self.startline = _get_name(lines[0])
        self.fields: dict[str, tuple[str, str, list[str]]] = _get_fields(lines)
        self.info: dict[str, tuple[str, str, list[str]]] = _get_fields(lines, True)
        self.start = start
        self.end = end
        self.start_comment = _get_comment(lines[1:])

    def get_fields(self) -> list[str]:
        """Returns the lines of the db associated with all fields

        Returns:
            list[str]: the lines of the db associated with all fields
        """
        field_lines = []
        for tuple in self.fields.values():
            field_lines = field_lines + [tuple[1]] + tuple[2]
        return field_lines

    def get_info(self) -> list[str]:
        """Returns the lines of the db associated with all info

        Returns:
            list[str]: the lines of the db associated with all info
        """
        info_lines = []
        for tuple in self.info.values():
            info_lines = info_lines + [tuple[1]] + tuple[2]
        return info_lines

    def add_field(self, name: str, val: str, comment: str = "") -> None:
        """Creates a new field with the name, value, and optionally comment.

        Fails if an field with the same name already exists.

        Args:
            name (str): The new field
            val (str): The value of the new field
            comment (str, optional): A comment to follow the info. Defaults to "".
        """
        if name in self.fields.keys():
            return
        else:
            if comment:
                comment = " #" + comment
            self.fields[name] = (val, f'    field({name}, "{val}"){comment}\n', [])

    def add_info(self, name: str, val: str, comment: str = "") -> None:
        """Creates a new info with the name, value, and optionally comment.

        Fails if an info with the same name already exists.

        Args:
            name (str): The new info
            val (str): The value of the new info
            comment (str, optional): A comment to follow the info. Defaults to "".
        """
        if name in self.info.keys():
            return
        else:
            if comment:
                comment = " #" + comment
            self.info[name] = (val, f'    info({name}, "{val}"){comment}\n', [])

    def delete_field(self, name: str) -> None:
        """Deletes a field, May cause loss of following multiline comments

        Args:
            name (str): The field to remove
        """
        if name in self.fields.keys():
            self.fields.pop(name)

    def delete_info(self, name: str) -> None:
        """Deletes an info, May cause loss of following multiline comments

        Args:
            name (str): The info to remove
        """
        if name in self.info.keys():
            self.info.pop(name)

    def change_field(self, name: str, val: str, comment: str = "") -> None:
        """Update the value and comment of a field.

        Args:
            name (str): the field to be updated.
            val (str): the new value of the field.
            comment (str, optional): A comment to follow the field. Defaults to "".
        """
        if name in self.fields.keys():
            line = self.fields[name][1]
            old_val = self.fields[name][0]
            old_multi_line_comment = self.fields[name][2]
            if comment:
                comment = " #" + comment
            new_line = f"{line.replace(old_val, val).rstrip()}{comment}\n"
            self.fields[name] = (val, new_line, old_multi_line_comment)

    def change_info(self, name: str, val: str, comment: str = "") -> None:
        """Update the value and comment of an info field.

        Args:
            name (str): the info to be updated.
            val (str): the new value of the info.
            comment (str, optional): A comment to follow the info. Defaults to "".
                Trailing multi-line comments are preserved.
        """
        if name in self.info.keys():
            line = self.info[name][1]
            old_val = self.info[name][0]
            old_multi_line_comment = self.info[name][2]
            if comment:
                comment = " #" + comment
            new_line = f"{line.replace(old_val, val).rstrip()}{comment}\n"
            self.info[name] = (val, new_line, old_multi_line_comment)

    def change_name(self, name: str) -> None:
        """Change the name of the record

        Args:
            name (str): The new name e.g. $(P)CS:DASHBOARD:BANNER:LEFT:VALUE
        """
        self.startline = self.startline.replace(self.name, name)
        self.name = name

    def change_type(self, type: str) -> None:
        """Change the type of the record

        Args:
            type (str): the new type i.e. mbbi
        """
        self.startline = self.startline.replace(self.type, type)
        self.type = type

    def update_record(self, db_file: list[str]) -> list[str]:
        """Method to update the record in the db file based on the record object

        Args:
            db_file (list[str]): The read in lines of the db file.

        Returns:
            list[str]: the lines of the db file with the record replaced with the updated version.
        """
        before_record = db_file[: self.start]
        after_record = db_file[1 + self.end :]

        new_db_lines = [self.startline]
        new_db_lines = new_db_lines + self.start_comment 
        new_db_lines = new_db_lines + self.get_fields()
        new_db_lines = new_db_lines + self.get_info()
        new_db_lines = new_db_lines + ["}\n"]
        new_db_lines = before_record + new_db_lines + after_record
        return new_db_lines

    def delete_record(self, db_file: list[str]) -> list[str]:
        """Method to remove the record object from the db

        Args:
            db_file (list[str]): The read in lines of the db file.

        Returns:
            list[str]: The lines of the db file without the record.
        """
        before_record = db_file[: self.start]
        after_record = db_file[1 + self.end :]
        return before_record + after_record


def read_file() -> list[str]:
    """Reads the dashboard.db into memory

    Returns:
        list[str]: list containing each line in dashboard.db
    """
    with open(DASHBOARD_DB_FILENAME) as db_file:
        return db_file.readlines()
    
def write_file(db_lines: list[str]) -> None:
    """writes db lines back into the file

    Returns:
        list[str]: list containing each line in dashboard.db
    """
    with open(DASHBOARD_DB_FILENAME, "w") as db_file:
        return db_file.writelines(db_lines)


def get_record(record_name: str, db_file: list[str]) -> Optional[Record]:
    """Given a record name generate a record object.

    Args:
        record_name (str): The name of the record to find (e.g. $(P)CS:DASHBOARD:BANNER:LEFT:VALUE)
        db_file (list[str]): The loaded in lines to check through

    Returns:
        Optional[Record]: A record object containing the information of the record,
        any comments inside it. or None if the record is not present or doesn't properly close.

    """
    name = re.escape(record_name)
    for i in range(0, len(db_file)):
        if re.match(rf"record\(.+, [\"\']{name}[\"\']\) {{", db_file[i]):
            end = get_end_of_record(db_file=db_file, line_number=i)
            if i == -1:
                return None
            else:
                return Record(db_file[i:end], i, end)
    return None


def get_end_of_record(db_file: list[str], line_number: int) -> int:
    """Given the first line of a record, return its end

    Args:
        db_file (list[str]): the list of strings loaded in from db
        line_number (int): The start of the record

    Returns:
        int: the line number of the closing } of the record.
    """
    for i in range(line_number, len(db_file)):
        if re.match(r"^([^#]|(\$\(.*=.*#.*\)))*}.*$", db_file[i]):
            return i
    return -1


def _get_fields(
    lines: list[str], info: bool = False
) -> dict[str, tuple[str, str, list[str]]]:
    """Takes a list of strings and extracts fields or info

    Args:
        lines (list[str]): The line to check (usually the lines of a record)
        info (bool, optional): Whether to search for fields or info

    Returns:
        dict[str, tuple[str, str, list[str]]]: returns a dictionary where the keys are the name/type
        of the fields, and the value is a tuple containing the value, the full line string, and a list
        of any following multi-line comments.
    """

    field_dict = {}
    if info:
        search = "info"
    else:
        search = "field"

    for index, line in enumerate(lines):
        if f"{search}(" in line:
            match = re.match(rf".*{search}\((.*), \"(.*)\"\).*", line)
            if match is not None:
                if index + 1 < len(lines):
                    _inner_tuple = (
                        str(match.group(2)),
                        f"{match.group(0)}\n",
                        _get_comment(lines[index + 1 :]),
                    )
                else:
                    _inner_tuple = (str(match.group(2)), f"{match.group(0)}\n", [])
                field_dict[str(match.group(1))] = _inner_tuple
    return field_dict


def _get_name(line: str) -> tuple[str, str, str]:
    """Get the name, type, and full first line of a record.

    Args:
        line (str): the line to check

    Returns:
        Optional[tuple[str, str, str]]: a tuple containing the name, type,
        and full string of a record definition, or None if fails regex
    """
    match = re.match(r".*record\((.*), \"(.*)\"\).*", line)
    if match is None:
        return ("", "", "")
    return match.group(1), match.group(2), f"{match.group(0)}\n"


def _get_comment(lines: list[str]) -> list[str]:
    """Get a whole line comment

    Checks for whole line comments or multi-line comments.

    Args:
        lines (list[str]): The lines to check (usually the entire record on from a starting point)

    Returns:
        list[str]: A list of consecutive comments i.e.
        ['#this comment \n' '#is on\n' ' #multiple lines']
    """
    multi_line_comment = []
    i = 0
    match = re.match(r"(\s*#.*)", lines[i])
    while match is not None:
        multi_line_comment.append(f"{match.group(0)}\n")
        i = i + 1
        if i < len(lines):
            match = re.match(r"(\s*#.*)", lines[i])
        else:
            match = None
    return multi_line_comment
