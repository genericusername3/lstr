"""Utility functions that deal with the sqlite database 'programs'."""

# SIJ (Sacroiliac joint) = ISG (Iliosakralgelenk)

from typing import Generator, Optional, Iterable, List, Dict, Any, Tuple

import os

from threading import Thread
import time

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

# Python 3.6 or higher is needed to retain dict order
PROGRAM_COLUMNS: Dict[str, Tuple[type, str]] = {
    "id": (int, "UNSIGNED BIG INT"),
    "pusher_left_distance_up": (int, "INT"),  # mm
    "pusher_left_distance_down": (int, "INT"),
    "pusher_right_distance_up": (int, "INT"),
    "pusher_right_distance_down": (int, "INT"),
    "pusher_left_speed_up": (int, "INT"),  # mm / s
    "pusher_left_speed_down": (int, "INT"),
    "pusher_right_speed_up": (int, "INT"),
    "pusher_right_speed_down": (int, "INT"),
    "pusher_left_delay_up": (int, "INT"),  # s
    "pusher_left_delay_down": (int, "INT"),
    "pusher_right_delay_up": (int, "INT"),
    "pusher_right_delay_down": (int, "INT"),
    "pusher_left_stay_duration_up": (int, "INT"),  # s
    "pusher_left_stay_duration_down": (int, "INT"),
    "pusher_right_stay_duration_up": (int, "INT"),
    "pusher_right_stay_duration_down": (int, "INT"),
    "pusher_left_push_count_up": (int, "INT"),
    "pusher_left_push_count_down": (int, "INT"),
    "pusher_right_push_count_up": (int, "INT"),
    "pusher_right_push_count_down": (int, "INT"),
    "pusher_left_distance_correction_up": (int, "INT"),  # mm / 7 deg
    "pusher_left_distance_correction_down": (int, "INT"),
    "pusher_right_distance_correction_up": (int, "INT"),
    "pusher_right_distance_correction_down": (int, "INT"),
    "angle_change_up": (int, "INT"),  # deg
    "angle_change_down": (int, "INT"),
    "push_distance_up": (int, "INT"),  # mm
    "push_distance_down": (int, "INT"),
    "push_count_up": (int, "INT"),
    "push_count_down": (int, "INT"),
    "pass_count_up": (int, "INT"),
    "pass_count_down": (int, "INT"),
}


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create tables
cursor.execute(
    "CREATE TABLE IF NOT EXISTS programs ("
    + ", ".join(
        [
            column + " " + datatype[1]
            for column, datatype in PROGRAM_COLUMNS.items()
        ]
    )
    + ")"
)

connection.commit()

atexit.register(connection.close)


class Program(GObject.Object):
    """A Program represents a database entry for a treatment program."""

    __dict: Dict[str, Any] = {}

    def __init__(self, program_dict: Dict[str, Any], **kwargs):
        """Create a new Program.

        This should never be manually done. To add a program to the database,
        use Program.add(). To get programs from the database, use
        Program.get() or Program.get_all().

        Args:
            program_dict (Dict[str, Any]): A dict representing the program.
                Keys and their corresponding expected types as in
                PROGRAM_COLUMNS
            **kwargs: Keyword arguments are added to program_dict
        """
        super().__init__()

        for key in PROGRAM_COLUMNS:
            if key in program_dict:
                if isinstance(program_dict[key], PROGRAM_COLUMNS[key][0]):
                    self.__dict[key] = program_dict[key]
                else:
                    raise TypeError(
                        f"The given program_dict has the key {key} "
                        + f"with type {type(key).__name__} "
                        + f"(should be: {PROGRAM_COLUMNS[key][0].__name__})"
                    )
            else:
                raise ValueError(
                    f"The given program_dict is missing the key {key} "
                    + f"(type: {PROGRAM_COLUMNS[key][0].__name__})"
                )

    @staticmethod
    def add(program_dict: Dict[str, Any], **kwargs) -> "Program":
        """Create a new Program and add it to the database.

        Args:
            program_dict (Dict[str, Any]): A dict representing the program.
                Keys and their corresponding expected types as in
                PROGRAM_COLUMNS
            **kwargs: Keyword arguments are added to program_dict
        """
        program_dict = program_dict.copy()

        program_dict["id"] = int(
            cursor.execute("SELECT MAX(id) FROM programs").fetchone()[0] or 0
        ) + 1

        program: Program = Program(program_dict)

        cursor.execute(
            f"INSERT INTO programs VALUES ({', '.join(['?' for _ in PROGRAM_COLUMNS])})",
            [program[key] for key in PROGRAM_COLUMNS],
        )

        connection.commit()

        return program

    @staticmethod
    def get_all() -> Generator["Program", None, None]:
        """Yield all programs in the database."""
        for program_row in cursor.execute(
            "SELECT " + ", ".join(PROGRAM_COLUMNS) + " FROM programs"
        ).fetchall():
            program_dict = {}
            for index, value in enumerate(program_row):
                program_dict[list(PROGRAM_COLUMNS.keys())[index]] = value

            yield Program(program_dict)

    @staticmethod
    def iter_to_model(program_iter: Iterable["Program"]) -> Gio.ListStore:
        """Convert an iterable of Program objects into a Gio.ListStore."""
        model: Gio.ListStore = Gio.ListStore()

        program_list: List[Program] = list(program_iter)

        def add_programs(program_list: List[Program]):
            if len(program_list):
                for program in program_list[:10]:
                    model.append(program)
                GLib.timeout_add(20, add_programs, program_list[10:])

        for program in program_list[:50]:
            model.append(program)

        # left out for perfomance reasons
        # add_programs(program_list[50:])

        return model

    def __getitem__(self, key):
        """Get a key from the patient. Syntax: Patient["<key>""] ."""
        return self.__dict.__getitem__(key)

    def __getattr__(self, name):
        """Get a key from the patient. Syntax: Patient.<key> ."""
        return self.__dict.__getitem__(name)


if __name__ == "__main__":
    import random

    for i in range(5):
        Program.add(
            {column: random.randint(0, 60) for column in PROGRAM_COLUMNS}
        )

        print("added " + str(i))

    print(list(Program.get_all()))
