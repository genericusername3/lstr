"""
Utility functions that deal with the sqlite database 'users'.

Focused on displaying users. More low-level user utility in auth_util.py
"""

from typing import Generator, Iterable, List, Union, Tuple

import os

from datetime import datetime

import sqlite3
import atexit

from gi.repository import GObject, Gio  # type: ignore

from . import auth_util


try:
    os.mkdir(os.path.expanduser("~/.liegensteuerung"))
except FileExistsError:
    pass
finally:
    os.chdir(os.path.expanduser("~/.liegensteuerung"))

DATABASE_NAME = "liegensteuerung.db"

DISPLAY_COLUMNS: Tuple[str, ...] = (
    "date",
    "program_id",
    "pain_location",
    "pain_intensity",
    "username",
)

connection = sqlite3.connect(DATABASE_NAME)
cursor = connection.cursor()
atexit.register(connection.close)


class Treatment(GObject.Object):
    """A Treatment represents a database entry for a treatment."""

    timestamp: int
    date: str
    program_id: int
    pain_intensity: int
    pain_location: str
    username: str

    def __init__(
        self,
        timestamp: int,
        program_id: int,
        pain_intensity: int,
        pain_location: str,
        username: str,
    ):
        """Create a new Treatment.

        This should never be manually done. To add a user to the database,
            use Patient.add_treatent_entry(). To get treatments from the
            database, use Treatment.get_all().

        Args:
            username (str): The user's username
            access_level (str): The user's access level.
                One of ('admin', 'doctor', 'helper')
        """
        super().__init__()

        self.timestamp = timestamp
        self.date = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
        self.program_id = program_id
        self.pain_intensity = pain_intensity
        self.pain_location = pain_location
        self.username = username

    @staticmethod
    def get_all() -> Generator["Treatment", None, None]:
        """Yield all users in the database."""
        for treatment_row in cursor.execute(
            """
                SELECT
                    timestamp,
                    program_id,
                    pain_intensity,
                    pain_location,
                    username
                FROM treatment_entries
            """
        ).fetchall():
            (
                timestamp,
                program_id,
                pain_intensity,
                pain_location,
                username,
            ) = treatment_row

            yield Treatment(
                timestamp, program_id, pain_intensity, pain_location, username
            )

    @staticmethod
    def iter_to_model(treatment_iter: Iterable["Treatment"]) -> Gio.ListStore:
        """Convert an iterable of Treatment objects into a Gio.ListStore.

        Args:
            treatment_iter (Iterable[Treatment]): An iterable of treatments to
                convert

        Returns:
            Gio.ListStore: The converted model
        """
        model: Gio.ListStore = Gio.ListStore()

        treatment_list: List[Treatment] = list(treatment_iter)

        for treatment in treatment_list:
            model.append(treatment)

        return model
