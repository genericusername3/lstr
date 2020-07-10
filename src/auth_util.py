"""Utility functions that deal with the sqlite database."""

import sqlite3
import atexit
import string
import random
import base64

from hashlib import sha512
from typing import Optional, Tuple


DATABASE_NAME = "liegensteuerung.db"


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

# Create table
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users
             (username TEXT, password_hash TEXT, salt TEXT)"""
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


def new_user(username: str, password: str) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        password (str): The user's password
    """
    if cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?", (username,)
    ).fetchone()[0]:
        raise ValueError("User already exists")

    salt: str = generate_salt()

    password_hash: str = base64.b64encode(
        sha512((password + salt).encode()).digest()
    ).decode()

    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?)", (username, password_hash, salt)
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


def modify_user(username: str, old_password: str, new_password: str) -> None:
    """Insert a new user into the database.

    Args:
        username (str): The user's username
        old_password (str): The user's old password
        new_password (str): The user's new password
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


if __name__ == "__main__":
    try:
        username = generate_salt()
        pwd = generate_salt()
        pwd2 = generate_salt()

        new_user(username, pwd)

        modify_user(username, pwd, pwd2)

        print([r for r in cursor.execute("SELECT * FROM users")])
    finally:
        connection.close()
