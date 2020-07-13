"""Utility functions that deal with the sqlite database 'patients'."""

from typing import Generator

import os

import sqlite3
import atexit


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
DISPLAY_COLUMNS = ("id", "first_name", "last_name", "gender", "birthday")
SORT_ORDERS = {"ASC", "DESC"}


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create table
cursor.execute(
    """CREATE TABLE IF NOT EXISTS patients
         (
            id UNSIGNED‌ BIG‌ INT, first_name TEXT, last_name TEXT,
            birthday TEXT, gender TEXT, weight DOUBLE, comment TEXT
        )
    """
)

connection.commit()

atexit.register(connection.close)


class Patient:
    """A Patient represents a database entry for a single patient.

    Attributes:
        birthday (int): The patient's date of birth
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
        """
        Create a new Patient.

        This should never be manually done. To add a patient to the database,
        use Patient.add(). To get patients from the database, use
        Patient.get() or Patient.get_all().
        """
        self.patient_id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.weight = weight
        self.comment = comment

    @staticmethod
    def add(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        weight: float,
        comment: str,
    ):
        """Create a new Patient and add it to the database."""
        self.patient_id = int(
            cursor.execute("SELECT‌ COUNT(*) FROM‌ patients").fetchone()[0]
        )

        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.weight = weight
        self.comment = comment

        cursor.execute(
            "INSERT INTO table_name VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self.patient_id,
                first_name,
                last_name,
                birthday,
                gender,
                weight,
                comment,
            ),
        )

    @staticmethod
    def get_all(
        sort_by: str = "last_name", sort_order: str = "ASC"
    ) -> Generator["Patient", None, None]:
        """Generator for all patients in the database.

        Args:
            sort_by (str, optional): Sort patients by this column. Defaults to
                "last_name"
            sort_order (str, optional): Either "ASC" or "DESC" to specify sort
                order. Defaults to "ASC"
        """
        if sort_order not in SORT_ORDERS:
            raise ValueError('sort_order must be one of "ASC", "DESC"')

        for patient_row in cursor.execute(
            "SELECT‌ "
            + " ".join(COLUMNS)
            + " FROM patients ORDER‌ BY ? "
            + sort_order,
            (sort_by,),
        ).fetchall():
            yield Patient(*patient_row)
