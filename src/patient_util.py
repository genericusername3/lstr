"""Utility functions that deal with the sqlite database 'patients'.

Attributes:
    COLUMNS (TYPE): Description
    connection (TYPE): Description
    cursor (TYPE): Description
    DATABASE_NAME (str): Description
    DISPLAY_COLUMNS (tuple): Description
    SORT_ORDERS (set): Description
"""

from typing import Generator, Optional, Iterable, List

import os

from threading import Thread

import sqlite3
import atexit

from gi.repository import GObject, GLib, Gio  # type: ignore


try:
    os.mkdir(os.path.expanduser("~/.liegensteuerung"))
except FileExistsError:
    pass
finally:
    os.chdir(os.path.expanduser("~/.liegensteuerung"))

DATABASE_NAME = "liegensteuerung.db"

COLUMNS = (
    "id",
    "first_name",
    "last_name",
    "birthday",
    "gender",
    "weight",
    "comment",
)

DISPLAY_COLUMNS = (
    "patient_id",
    "first_name",
    "last_name",
    "gender",
    "birthday",
)

DATE_COLUMNS = {"birthday"}

SORT_ORDERS = {"ASC", "DESC"}


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create table
cursor.execute(
    """CREATE TABLE IF NOT EXISTS patients
         (
            id UNSIGNED BIG INT, first_name TEXT, last_name TEXT,
            birthday TEXT, gender TEXT, weight DOUBLE, comment TEXT
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
    ):
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
                cursor.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
            ),
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

    @staticmethod
    def get_all() -> Generator["Patient", None, None]:
        """Yield all patients in the database."""

        for patient_row in cursor.execute(
            "SELECT " + ", ".join(COLUMNS) + " FROM patients"
        ).fetchall():
            yield Patient(*patient_row)

    @staticmethod
    def get(
        patient_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birthday: Optional[str] = None,
        gender: Optional[str] = None,
        weight: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> "Patient":
        """Search for patients that match the given parameters.

        Args:
            patient_id (int): An ID to search for
            first_name (str): A first name to search for
            last_name (str): A last name to search for
            birthday (str): A date of birth to search for
            gender (str): A gender to search for
            weight (float): A weight in kilograms to search for
            comment (str): A comment to search for
        """
        ...
        raise NotImplementedError

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

        # add_patients(patient_list[50:])

        return model


if __name__ == "__main__":
    import names  # type: ignore
    import random

    for i in range(500):
        first_name: str
        gender: str

        if random.randint(0, 1) == 1:
            first_name = names.get_first_name(gender='male')
            gender = "Männlich"
        else:
            first_name = names.get_first_name(gender='female')
            gender = "Weiblich"

        Patient.add(
            first_name=first_name,
            last_name=names.get_last_name(),
            birthday="1970-01-01",
            gender=gender,
            weight=65 + (random.randint(0, 200) / 10.0),
            comment="",
        )

        print("added " + first_name)
