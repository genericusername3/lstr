"""
Utility functions that deal with the sqlite database 'users'.

Focused on displaying users. More low-level user utility in auth_util.py
"""

from typing import Generator, Iterable, List, Union, Tuple

import os

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

DISPLAY_COLUMNS: Tuple[str, ...] = ("username", "access_level")

connection = sqlite3.connect(DATABASE_NAME)
cursor = connection.cursor()
atexit.register(connection.close)


class User(GObject.Object):
    """A User represents a database entry for a user."""

    username: str
    access_level: str

    def __init__(self, username: str, access_level: Union[str, int]):
        """Create a new User.

        This should never be manually done. To add a user to the database,
            use auth_util.new_user(). To get users from the database, use
            User.get_all().

        Args:
            username (str): The user's username
            access_level (str): The user's access level.
                One of ('admin', 'doctor', 'helper')
        """
        super().__init__()

        self.username = username

        if isinstance(access_level, int):
            if access_level in auth_util.ACCESS_LEVELS.values():
                access_level = auth_util.ACCESS_LEVEL_NAMES[access_level]
            else:
                raise ValueError(
                    f"{access_level} is not a valid access level id"
                )

        if access_level not in auth_util.ACCESS_LEVELS:
            raise ValueError(f"{access_level} is not a valid access level")

        self.access_level = access_level

    @staticmethod
    def get_all() -> Generator["User", None, None]:
        """Yield all users in the database."""
        for user_row in cursor.execute(
            "SELECT username, access_level FROM users"
        ).fetchall():
            username: str = user_row[0]
            access_level: int = user_row[1]

            yield User(username, access_level)

    @staticmethod
    def iter_to_model(user_iter: Iterable["User"]) -> Gio.ListStore:
        """Convert an iterable of User objects into a Gio.ListStore.

        Args:
            user_iter (Iterable[User]): An iterable of users to convert

        Returns:
            Gio.ListStore: The converted model
        """
        model: Gio.ListStore = Gio.ListStore()

        user_list: List[User] = list(user_iter)

        for user in user_list:
            model.append(user)

        return model
