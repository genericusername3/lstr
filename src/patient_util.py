"""Utility functions that deal with the sqlite database 'patients'.

Attributes:
    COLUMNS (TYPE): Description
    connection (TYPE): Description
    cursor (TYPE): Description
    DATABASE_NAME (str): Description
    DISPLAY_COLUMNS (tuple): Description
    SORT_ORDERS (set): Description
"""

from typing import (
    Generator,
    Dict,
    Iterable,
    List,
    Set,
    Optional,
    Tuple,
    Any,
    Callable,
)

import os

from threading import Thread
import time

import sqlite3
import atexit

from gi.repository import GObject, GLib, Gio  # type: ignore


GENDERS: Dict[str, str] = {
    "male": "Männlich",
    "female": "Weiblich",
    "other": "Divers",
}


try:
    from . import program_util
except ImportError:
    import program_util


try:
    os.mkdir(os.path.expanduser("~/.liegensteuerung"))
except FileExistsError:
    pass
finally:
    os.chdir(os.path.expanduser("~/.liegensteuerung"))

DATABASE_NAME = "liegensteuerung.db"

COLUMNS: List[str] = [
    "id",
    "first_name",
    "last_name",
    "birthday",
    "gender",
    "weight",
    "comment",
]

DISPLAY_COLUMNS: List[str] = [
    "patient_id",
    "last_name",
    "first_name",
    "gender_translated",
    "birthday",
]

DATE_COLUMNS: Set[str] = {"birthday"}

TREATMENT_COLUMNS: List[str] = [
    "patient_id",
    "program_id",
    "username",
    "timestamp",
    "pain_intensity",
    "pain_location",
]

SORT_ORDERS = {"ASC", "DESC"}


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create tables
cursor.execute(
    """CREATE TABLE IF NOT EXISTS patients
         (
            id UNSIGNED BIG INT, first_name TEXT, last_name TEXT,
            birthday TEXT, gender TEXT, weight DOUBLE, comment TEXT
        )
    """
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS treatment_entries
        (
            patient_id UNSIGNED BIG INT, program_id UNSIGNED BIG INT,
            timestamp UNSIGNED BIG INT, pain_intensity INT, pain_location TEXT
        )
    """
)

connection.commit()

atexit.register(connection.close)


class Patient(GObject.Object):
    """A Patient represents a database entry for a single patient.

    Attributes:
        birthday (str): The patient's date of birth
        comment (str): A comment
        first_name (str): The patient's first name
        gender (str): The patient's gender
        last_name (str): The patient's last name
        patient_id (int): An assigned ID
        weight (float): The patient's weight in kilograms
    """

    patient_id: int
    first_name: str
    last_name: str
    birthday: str
    gender: str
    gender_translated: str
    weight: float
    comment: str

    def __init__(
        self,
        patient_id: int,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        weight: float,
        comment: str,
    ):
        """Create a new Patient.

        This should never be manually done. To add a patient to the database,
        use Patient.add(). To get patients from the database, use
        Patient.get() or Patient.get_all().

        Args:
            patient_id (int): An assigned ID
            first_name (str): The patient's first name
            last_name (str): The patient's last name
            birthday (str): The patient's date of birth
            gender (str): The patient's gender
            weight (float): The patient's weight in kilograms
            comment (str): A comment
        """
        super().__init__()

        self.patient_id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.gender_translated = GENDERS[gender]
        self.weight = weight
        self.comment = comment

    @staticmethod
    def add(
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        weight: float,
        comment: str,
    ) -> "Patient":
        """Create a new Patient and add it to the database.

        Args:
            first_name (str): The patient's first name
            last_name (str): The patient's last name
            birthday (str): The patient's date of birth
            gender (str): The patient's gender
            weight (float): The patient's weight in kilograms
            comment (str): A comment
        """
        patient = Patient(
            patient_id=int(
                cursor.execute("SELECT MAX(id) FROM patients").fetchone()[0]
                or 0
            )
            + 1,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            weight=weight,
            comment=comment,
        )

        cursor.execute(
            "INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                patient.patient_id,
                patient.first_name,
                patient.last_name,
                patient.birthday,
                patient.gender,
                patient.weight,
                patient.comment,
            ),
        )

        connection.commit()

        return patient

    def modify(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birthday: Optional[str] = None,
        gender: Optional[str] = None,
        weight: Optional[float] = None,
        comment: Optional[str] = None,
    ):
        """Modify the patient and save to the database.

        Args:
            first_name (str, optional): The patient's first name or
                None (default) to not change
            last_name (str, optional): The patient's last name or
                None (default) to not change
            birthday (str, optional): The patient's date of birth or
                None (default) to not change
            gender (str, optional): The patient's gender or None (default) to
                not change
            weight (float, optional): The patient's weight in kilograms o
                None (default) to not change
            comment (str, optional): A comment or None (default) to not change
        """
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if birthday is not None:
            self.birthday = birthday
        if gender is not None:
            self.gender = gender
        if weight is not None:
            self.weight = weight
        if comment is not None:
            self.comment = comment

        cursor.execute(
            """
                UPDATE patients
                SET first_name = ?,
                    last_name = ?,
                    birthday = ?,
                    gender = ?,
                    weight = ?,
                    comment = ?
                WHERE id=?
            """,
            (
                self.first_name,
                self.last_name,
                self.birthday,
                self.gender,
                self.weight,
                self.comment,
                self.patient_id,
            ),
        )

        connection.commit()

    @staticmethod
    def sort(
        patient_rows: Iterable[Tuple[Any, ...]],
        sort_key_func: Optional[Callable] = None,
        reverse: Optional[bool] = False,
    ) -> List[Tuple[Any, ...]]:
        """Sort an iterable of patient rows.

        If sort_key_func is None, order is retained (if reverse is True,
            return patient_rows[::-1]).

        Args:
            patient_rows (Iterable[Tuple[Any, ...]]): Rows to sort
            sort_key_func (Optional[Callable]): A callable that
                returns a value by which to sort the rows
            reverse (Optional[bool]): Whether to reverse the sorted
                iterable

        Returns:
            Iterable[Tuple[Any, ...]]: The sorted iterable
        """
        sorted_patient_rows: List[Tuple[Any, ...]]

        if sort_key_func is None:
            sorted_patient_rows = list(patient_rows)
        else:
            sorted_patient_rows = sorted(patient_rows, key=sort_key_func)

        if reverse:
            return sorted_patient_rows[::-1]
        return sorted_patient_rows

    @staticmethod
    def get_all(
        sort_key_func: Optional[Callable] = None, reverse: bool = False
    ) -> Generator["Patient", None, None]:
        """Yield all patients in the database.

        Args:
            sort_key_func (Optional[Callable]): A callable that
                returns a value by which to sort the rows
            reverse (Optional[bool]): Whether to reverse the sorted
                iterable
        """
        for patient_row in Patient.sort(
            cursor.execute(
                "SELECT " + ", ".join(COLUMNS) + " FROM patients"
            ).fetchall(),
            sort_key_func,
            reverse,
        ):
            yield Patient(*patient_row)

    @staticmethod
    def get_for_query(
        query: str,
        sort_key_func: Optional[Callable] = None,
        reverse: bool = False,
    ) -> Generator["Patient", None, None]:
        """Yield all patients in the database.

        Args:
            query (str): A query to match
            sort_key_func (Optional[Callable]): A callable that
                returns a value by which to sort the rows
            reverse (Optional[bool]): Whether to reverse the sorted
                iterable
        """
        patient_rows: Set[Tuple[Any, ...]] = set()

        for word in query.split(" "):
            for patient_row in Patient.get_for_query_word(word):
                patient_rows.add(patient_row)

        for patient_row in Patient.sort(patient_rows, sort_key_func, reverse):
            yield Patient(*patient_row)

    @staticmethod
    def get_for_query_word(
        query_word: str,
        sort_key_func: Optional[Callable] = None,
        reverse: bool = False,
    ) -> Generator[Tuple[Any, ...], None, None]:
        """Yield all patients in the database.

        Args:
            query_word (str): The word to match
            sort_key_func (Optional[Callable]): A callable that
                returns a value by which to sort the rows
            reverse (Optional[bool]): Whether to reverse the sorted
                iterable
        """
        for patient_row in Patient.sort(
            cursor.execute(
                f"""
                SELECT {", ".join(COLUMNS)}
                FROM patients
                WHERE last_name LIKE ("%" || ? || "%")
                OR first_name LIKE ("%" || ? || "%")
                OR id LIKE ("%" || ? || "%")
            """,
                (query_word.lower(), query_word.lower(), query_word.lower()),
            ).fetchall(),
            sort_key_func,
            reverse,
        ):
            yield tuple(patient_row)

    @staticmethod
    def iter_to_model(patient_iter: Iterable["Patient"]) -> Gio.ListStore:
        """Convert an iterable of Patient objects into a Gio.ListStore."""
        model: Gio.ListStore = Gio.ListStore()

        patient_list: List[Patient] = list(patient_iter)

        def add_patients(patient_list: List[Patient]):
            if len(patient_list):
                for patient in patient_list[:10]:
                    model.append(patient)
                GLib.timeout_add(20, add_patients, patient_list[10:])

        for patient in patient_list[:50]:
            model.append(patient)

        # left out for perfomance reasons
        # add_patients(patient_list[50:])

        return model

    def add_pain_entry(
        self, username: str, pain_intensity: int, pain_location: str,
    ) -> int:
        """Add a pain entry to the database.

        A pain entry with the patient id, the two pain values and
            time.time() will be added to the table treatment_entries

        Args:
            username (str): The treating user's username
            pain_intensity (int): The pain intensity
            pain_location (str): Where the pain is; one of "left",
                "left-right", "both", "right-left", "right"

        Returns:
            int: The UNIX timestamp used for the entry

        Raises:
            ValueError: If the pain values provided are invalid
        """
        if pain_intensity not in range(11):
            raise ValueError(
                "pain_intensity must be between 0 and 10 (inclusive)"
            )
        if int(pain_intensity) != pain_intensity:
            raise ValueError("pain_intensity must be an int")

        timestamp: int = int(time.time())

        cursor.execute(
            """
                INSERT INTO treatment_entries
                    (patient_id, timestamp, pain_intensity, pain_location)
                VALUES
                    (?, ?, ?, ?)
            """,
            (self.patient_id, timestamp, pain_intensity, pain_location),
        )
        connection.commit()

        return timestamp

    def add_treatment_entry(
        self, timestamp: int, username: str, program: program_util.Program,
    ) -> int:
        """Add a program entry to the database.

        A program entry with the patient id, the program number and
            time.time() will be added to the table treatment_entries

        Args:
            timestamp (int): The UNIX timestamp of an existing treatment entry
                (with pain values)
            username (str): The treating user's username
            program (program_util.Program): The program that was completed

        Returns:
            int: The UNIX timestamp used for the entry
        """
        new_timestamp: int = int(time.time())

        cursor.execute(
            """
            UPDATE treatment_entries
            SET program_id = ?, timestamp = ?
            WHERE patient_id=? AND timestamp=?
            """,
            (program.id, new_timestamp, self.patient_id, timestamp,),
        )
        connection.commit()

        return new_timestamp

    def modify_pain_entry(
        self,
        timestamp: int,
        username: str,
        pain_intensity: int,
        pain_location: str,
    ) -> int:
        """Modify a pain entry in the database.

        The pain entry with the timestamp will be modified to have
            pain_intensity and pain_location instead of its old values.

        If the entry doesn't exist, do nothing.

        Args:
            timestamp (int): The UNIX timestamp of the entry to modify
            username (str): The treating user's username
            pain_intensity (int): The pain intensity
            pain_location (str): Where the pain is; one of "left",
                "left-right", "both", "right-left", "right"

        Returns:
            int: The new UNIX timestamp used for the entry

        Raises:
            ValueError: If the pain values provided are invalid
        """
        if pain_intensity not in range(11):
            raise ValueError("pain_left must be between 0 and 10 (inclusive)")
        if int(pain_intensity) != pain_intensity:
            raise ValueError("pain_left must be an int")

        new_timestamp: int = int(time.time())

        cursor.execute(
            """
                UPDATE treatment_entries
                SET pain_intensity = ?, pain_location = ?, timestamp = ?
                WHERE patient_id=? AND timestamp=?
            """,
            (
                pain_intensity,
                pain_location,
                new_timestamp,
                self.patient_id,
                timestamp,
            ),
        )
        connection.commit()

        return new_timestamp


if __name__ == "__main__":
    import names  # type: ignore
    import random

    for i in range(75):
        first_name: str
        gender: str

        if random.randint(0, 1) == 1:
            first_name = names.get_first_name(gender="male")
            gender = "male"
        else:
            first_name = names.get_first_name(gender="female")
            gender = "female"

        p: Patient = Patient.add(
            first_name=first_name,
            last_name=names.get_last_name(),
            birthday="1970-01-01",
            gender=gender,
            weight=65 + (random.randint(0, 200) / 10.0),
            comment="",
        )

        print("added " + first_name)

        timestamp = p.add_pain_entry(
            random.randint(0, 10),
            random.choice(
                ("left", "left-right", "both", "right-left", "right")
            ),
        )

        p.add_treatment_entry(
            timestamp, program_util.Program.get_all().__next__(),
        )
