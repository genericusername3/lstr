"""Utility functions that deal with the sqlite database 'patients'.

Attributes:
    COLUMNS (TYPE): Description
    connection (TYPE): Description
    cursor (TYPE): Description
    DATABASE_NAME (str): Description
    DISPLAY_COLUMNS (tuple): Description
    SORT_ORDERS (set): Description
"""

from typing import Generator, Dict, Iterable, List, Set

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
    "first_name",
    "last_name",
    "gender_translated",
    "birthday",
]

DATE_COLUMNS: Set[str] = {"birthday"}

TREATMENT_COLUMNS: List[str] = [
    "patient_id",
    "program_id",
    "timestamp",
    "vas",
    "sij_left",
    "sij_right",
    "sij_both",
    "sij_left_right",
    "sij_right_left",
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
    """CREATE TABLE IF NOT EXISTS pain_entries
         (
            patient_id UNSIGNED BIG INT, timestamp UNSIGNED‌ BIG‌ INT,
            pain_left INT, pain_right INT
        )
    """
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS treatment_entries
        (
            patient_id UNSIGNED BIG INT, program_id UNSIGNED BIG INT,
            timestamp UNSIGNED BIG INT,

            vas INT,

            sij_left INT, sij_right INT, sij_both INT, sij_left_right INT,
            sij_right_left INT
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

    @staticmethod
    def get_all() -> Generator["Patient", None, None]:
        """Yield all patients in the database."""
        for patient_row in cursor.execute(
            "SELECT " + ", ".join(COLUMNS) + " FROM patients"
        ).fetchall():
            yield Patient(*patient_row)

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

    def add_pain_entry(self, pain_left: int, pain_right: int) -> int:
        """Add a pain entry to the database.

        A pain entry with the patient id, the two pain values and
            time.time() will be added to the table pain_entries

        Args:
            pain_left (int): The pain value for the left side
            pain_right (int): The pain value for the right side

        Returns:
            int: The UNIX timestamp used for the entry

        Raises:
            ValueError: If the pain values provided are invalid
        """
        if pain_left not in range(11):
            raise ValueError("pain_left must be between 0 and 10 (inclusive)")
        if int(pain_left) != pain_left:
            raise ValueError("pain_left must be an int")

        if pain_right not in range(11):
            raise ValueError("pain_right must be between 0 and 10 (inclusive)")
        if int(pain_right) != pain_right:
            raise ValueError("pain_right must be an int")

        timestamp: int = int(time.time())

        cursor.execute(
            "INSERT INTO pain_entries VALUES (?, ?, ?, ?)",
            (self.patient_id, timestamp, pain_left, pain_right),
        )
        connection.commit()

        return timestamp

    def add_treatment_entry(
        self,
        program: program_util.Program,
        vas: str,
        sij_left: str,
        sij_right: str,
        sij_both: str,
        sij_left_right: str,
        sij_right_left: str,
    ) -> int:
        """Add a program entry to the database.

        A program entry with the patient id, the program number and
            time.time() will be added to the table pain_entries

        Args:
            program (program_util.Program): The program that was completed
            vas (str): The value for the vas column
            sij_left (str): The value for the sij_left column
            sij_right (str): The value for the sij_right column
            sij_both (str): The value for the sij_both column
            sij_left_right (str): The value for the sij_left_right column
            sij_right_left (str): The value for the sij_right_left column

        Returns:
            int: The UNIX timestamp used for the entry
        """
        timestamp: int = int(time.time())

        cursor.execute(
            "INSERT INTO treatment_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.patient_id,
                program.id,
                timestamp,
                vas,
                sij_left,
                sij_right,
                sij_both,
                sij_left_right,
                sij_right_left,
            ),
        )
        connection.commit()

        return timestamp

    def modify_pain_entry(
        self, timestamp: int, pain_left: int, pain_right: int
    ) -> int:
        """Modify a pain entry in the database.

        The pain entry with the timestamp will be modified to have pain_left
            and pain_right instead of its old values.

        If the entry doesn't exist, do nothing.

        Args:
            timestamp (int): The UNIX timestamp of the entry to modify
            pain_left (int): The pain value for the left side
            pain_right (int): The pain value for the right side

        Returns:
            int: The new UNIX timestamp used for the entry

        Raises:
            ValueError: If the pain values provided are invalid
        """
        if pain_left not in range(11):
            raise ValueError("pain_left must be between 0 and 10 (inclusive)")
        if int(pain_left) != pain_left:
            raise ValueError("pain_left must be an int")

        if pain_right not in range(11):
            raise ValueError("pain_right must be between 0 and 10 (inclusive)")
        if int(pain_right) != pain_right:
            raise ValueError("pain_right must be an int")

        new_timestamp: int = int(time.time())

        cursor.execute(
            """
                UPDATE pain_entries
                SET pain_left = ?, pain_right = ?, timestamp = ?
                WHERE patient_id=? AND timestamp=?
            """,
            (pain_left, pain_right, new_timestamp, self.patient_id, timestamp),
        )
        connection.commit()

        return new_timestamp

    def modify_treatment_entry(
        self,
        timestamp: int,
        program: program_util.Program,
        vas: str,
        sij_left: str,
        sij_right: str,
        sij_both: str,
        sij_left_right: str,
        sij_right_left: str,
    ) -> int:
        """Modify a treatment entry in the database.

        The treatment entry with the timestamp and program id will be modified
            to have the new column values.

        If the entry doesn't exist, do nothing.

        Args:
            timestamp (int): The UNIX timestamp of the entry to modify
            program (program_util.Program): The new program
            vas (str): The new value for the vas column
            sij_left (str): The new value for the sij_left column
            sij_right (str): The new value for the sij_right column
            sij_both (str): The new value for the sij_both column
            sij_left_right (str): The new value for the sij_left_right column
            sij_right_left (str): The new value for the sij_right_left column

        Returns:
            int: The new UNIX timestamp used for the entry
        """
        new_timestamp: int = int(time.time())

        cursor.execute(
            """
                UPDATE treatment_entries
                SET
                    vas = ?,
                    sij_left = ?,
                    sij_right = ?,
                    sij_both = ?,
                    sij_left_right = ?,
                    sij_right_left = ?,
                WHERE
                    patient_id=?
                    AND‌ program_id=?
                    AND timestamp=?
            """,
            (
                vas,
                sij_left,
                sij_right,
                sij_both,
                sij_left_right,
                sij_right_left,
                self.patient_id,
                program.id,
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

        p.add_treatment_entry(
            program_util.Program.get_all().__next__(),
            vas="VAS",
            sij_left="sij_left",
            sij_right="sij_right",
            sij_both="sij_both",
            sij_left_right="sij_left_right",
            sij_right_left="sij_right_left",
        )
