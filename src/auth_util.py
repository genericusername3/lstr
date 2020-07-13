"""Utility functions that deal with the sqlite database 'users'."""

import os

import sqlite3
import atexit
import string
import random
import base64

from hashlib import sha512
from typing import Optional, Tuple


try:
    os.mkdir(os.path.expanduser("~/.liegensteuerung"))
except FileExistsError:
    pass
finally:
    os.chdir(os.path.expanduser("~/.liegensteuerung"))

DATABASE_NAME = "liegensteuerung.db"

ACCESS_LEVELS = {"admin": 2, "expert": 1, "user": 0}


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create table
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users
         (username TEXT, password_hash TEXT, salt TEXT, access_level INT)"""
)

connection.commit()

atexit.register(connection.close)


def generate_salt(length: int = 32) -> str:
    """Generate a pseudo-random string (consisting of ASCII letters).

    Args:
        length (int, optional): The length of the string to generate

    Returns:
        str: A random string. Can be used as a salt.
    """
    return "".join(
        [random.choice(string.ascii_letters) for _ in range(length)]
    )


def does_admin_exist() -> bool:
    """Return whether an admin account exists.

    Returns:
        bool: Whether an admin account exists.
    """
    return cursor.execute(
        "SELECT COUNT(*) FROM users WHERE access_level = ?",
        (ACCESS_LEVELS["admin"],),
    ).fetchone()[0]


def new_user(
    username: str,
    password: str,
    access_level: str,
    admin_username: Optional[str] = None,
    admin_password: Optional[str] = None,
) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        password (str): The user's password
        access_level (str): The user's access level. One of ACCESS_LEVELS
        admin_username (str, optional): An administrator's username
            or None if no admin exists. Defaults to None
        admin_password (str, optional): An administrator's password
            or None if no admin exists. Defaults to None

    Raises:
        ValueError: if admin credentials are wrong or missing.
    """
    if does_admin_exist():
        if admin_username is None or admin_password is None:
            raise ValueError(
                "Admin credentials may not be None if an admin exists."
            )
        elif not authenticate(admin_username, admin_password):
            raise ValueError("Admin password invalid")

        elif get_access_level(admin_username) != "admin":
            raise ValueError(
                "Given admin does not have sufficient permissions"
            )

    if cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?", (username,)
    ).fetchone()[0]:
        raise ValueError("User already exists")

    salt: str = generate_salt()

    password_hash: str = base64.b64encode(
        sha512((password + salt).encode()).digest()
    ).decode()

    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        (username, password_hash, salt, ACCESS_LEVELS[access_level]),
    )
    connection.commit()


def authenticate(username: str, password: str) -> bool:
    """Verify a user's password.

    Args:
        username (str): The user's username
        password (str): The user's password

    Returns:
        bool: True if the password is correct, False otherwise

    Raises:
        ValueError: if the username is invalid
    """
    user_entry: Optional[Tuple[str, str]] = cursor.execute(
        "SELECT salt, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if user_entry is None:
        raise ValueError("Username invalid")

    salt: str
    correct_password_hash: str
    salt, correct_password_hash = user_entry

    password_hash: str = base64.b64encode(
        sha512((password + salt).encode()).digest()
    ).decode()

    return password_hash == correct_password_hash


def get_access_level(username: str) -> str:
    """Get a user's access level.

    Args:
        username (str): The user's username

    Returns:
        str: The user's access level

    Raises:
        ValueError: if the username is invalid
    """
    user_entry: Optional[Tuple[str, str]] = cursor.execute(
        "SELECT access_level FROM users WHERE username = ?", (username,),
    ).fetchone()

    if user_entry is None:
        raise ValueError("Username invalid")

    access_level: str = user_entry[0]

    return [
        key for key in ACCESS_LEVELS if ACCESS_LEVELS[key] == access_level
    ][0]


def modify_password(
    username: str, old_password: str, new_password: str
) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        old_password (str): The user's old password
        new_password (str): The user's new password

    No Longer Raises:
        ValueError: if the old credentials are invalid
    """
    if not authenticate(username, old_password):
        raise ValueError("Password invalid")

    new_salt: str = generate_salt()

    new_password_hash: str = base64.b64encode(
        sha512((new_password + new_salt).encode()).digest()
    ).decode()

    cursor.execute(
        "UPDATE users SET salt = ?, password_hash = ? WHERE username = ?",
        (new_salt, new_password_hash, username),
    )
    connection.commit()


def modify_access_level(
    username: str, access_level: str, admin_username: str, admin_password: str
) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        access_level (str): The new access level for the user
        admin_username (str): An admin's username
        admin_password (str): An admin's password

    No Longer Raises:
        ValueError: if the admin credentials are invalid
    """
    if not authenticate(admin_username, admin_password):
        raise ValueError("Admin password invalid")
    if get_access_level(admin_username) != "admin":
        raise ValueError("Given admin does not have sufficient permissions")

    cursor.execute(
        "UPDATE users SET access_level = ? WHERE username = ?",
        (ACCESS_LEVELS[access_level], username),
    )
    connection.commit()


def modify_password_from_admin(
    username: str, new_password: str, admin_username: str, admin_password: str
) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        new_password (str): The user's new password
        admin_username (str): An administrator's username
            or None if no admin exists. Defaults to None
        admin_password (str): An administrator's password
            or None if no admin exists. Defaults to None

    Deleted Parameters:
        old_password (str): The user's old password
    """
    if not authenticate(admin_username, admin_password):
        raise ValueError("Admin password invalid")
    if get_access_level(admin_username) != "admin":
        raise ValueError("Given admin does not have sufficient permissions")

    new_salt: str = generate_salt()

    new_password_hash: str = base64.b64encode(
        sha512((new_password + new_salt).encode()).digest()
    ).decode()

    cursor.execute(
        "UPDATE users SET salt = ?, password_hash = ? WHERE username = ?",
        (new_salt, new_password_hash, username),
    )
    connection.commit()
