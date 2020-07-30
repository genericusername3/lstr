"""Util functions for showing/hiding a virtual keyboard."""

from subprocess import call
from threading import Timer
from typing import Optional
from time import sleep

from gi.repository import Gtk  # type: ignore


keyboard_shown: bool = False
keyboard_needed: bool = False

update_timer: Optional[Timer] = None

UPDATE_DELAY: float = 0.1
KEYBOARD_REACT_DELAY: float = 0.2

keyboard_revealer: Optional[Gtk.Revealer] = None


def set_keyboard(keyboard: Gtk.Revealer) -> None:
    """Set the Gtk.Revealer that contains the on-screen keyboard.

    Args:
        keyboard (Gtk.Revealer): A Gtk.Revealer that can be revealed to show
            the keyboard (and unrevealed to hide it)
    """
    global keyboard_revealer

    keyboard_revealer = keyboard


def request_keyboard() -> None:
    """Request the virtual keyboard to be shown."""
    global keyboard_needed, update_timer

    keyboard_needed = True

    if update_timer is not None:
        update_timer.cancel()

        if update_timer.is_alive():
            update_timer.join()

    update_timer = Timer(UPDATE_DELAY, update_keyboard)
    update_timer.start()


def unrequest_keyboard() -> None:
    """Request the virtual keyboard to be hidden."""
    global keyboard_needed, update_timer

    keyboard_needed = False

    if update_timer is not None:
        update_timer.cancel()

        if update_timer.is_alive():
            update_timer.join()

    update_timer = Timer(UPDATE_DELAY, update_keyboard)
    update_timer.start()


def toggle_keyboard_request() -> None:
    """Toggle whether the virtual keyboard is requested."""
    global keyboard_needed, update_timer

    keyboard_needed = not keyboard_shown

    if update_timer is not None:
        update_timer.cancel()

        if update_timer.is_alive():
            update_timer.join()

    update_timer = Timer(UPDATE_DELAY, update_keyboard)
    update_timer.start()


def update_keyboard() -> None:
    """Show or hide the keyboard according to whether it is needed."""
    if keyboard_shown != keyboard_needed:
        if keyboard_needed:
            show_keyboard()
        else:
            hide_keyboard()


def show_keyboard() -> None:
    """Show the virtual keyboard."""
    global keyboard_shown

    if keyboard_revealer is None:
        raise ValueError(
            "You must call set_keyboard to set a keyboard revealer first."
        )

    else:
        keyboard_revealer.set_reveal_child(True)

    sleep(KEYBOARD_REACT_DELAY)

    keyboard_shown = True


def hide_keyboard() -> None:
    """Hide the virtual keyboard."""
    global keyboard_shown

    if keyboard_revealer is None:
        raise ValueError(
            "You must call set_keyboard to set a keyboard revealer first."
        )

    else:
        keyboard_revealer.set_reveal_child(False)

    sleep(KEYBOARD_REACT_DELAY)

    keyboard_shown = False


if __name__ == "__main__":
    import time

    show_keyboard()
    time.sleep(1)
    hide_keyboard()
