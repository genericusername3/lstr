"""A page that prompts the user to register."""

from typing import Dict

import abc

import time

from gi.repository import Gdk, Gtk  # type: ignore

from . import osk_util
from .opcua_util import Connection


LONG_PRESS_TIME = 0.5  # seconds


class PageClass(abc.ABCMeta, type(Gtk.Box)):
    pass


class Page(abc.ABC):
    """An abstract page superclass that prompts the user to register.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        is_patient_info_page (bool): whether the Page shows one patient's info,
            i.e. a Page with this set to True will not have a patient button in
            the header bar
        title (str): The Page's title
    """

    is_patient_info_page: bool = False

    _entries_pressed: Dict[Gtk.Entry, float] = {}

    @property
    @abc.abstractmethod
    def header_visible(self) -> bool:
        """Whether the window header bar should be visible for this page."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def title(self) -> str:
        """Title of this page shown in the window header bar."""
        raise NotImplementedError

    @abc.abstractmethod
    def prepare(self, *args, **kwargs) -> None:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take
        """
        raise NotImplementedError

    def unprepare(self) -> None:
        """Prepare the page to be hidden."""
        pass

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        pass

    def on_focus_entry(
        self, widget: Gtk.Widget, event: Gdk.EventFocus
    ) -> None:
        """React to an entry being focused. Show an on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        osk_util.request_keyboard()

    def on_entry_button_press(
        self, widget: Gtk.Widget, event: Gdk.EventButton
    ) -> None:
        """React to an entry being clicked (button press).

        Args:
            widget (Gtk.Widget): The clicked entry.
            event (Gdk.EventFocus): The button press event.
        """
        if widget.is_focus():
            self._entries_pressed[widget] = time.time()

    def on_entry_button_release(
        self, widget: Gtk.Widget, event: Gdk.EventButton
    ) -> None:
        """React to an entry being unclicked (button release). Toggle OSK.

        Args:
            widget (Gtk.Widget): The clicked entry.
            event (Gdk.EventFocus): The button press event.
        """
        if time.time() < self._entries_pressed.get(widget, 0) + LONG_PRESS_TIME:
            osk_util.toggle_keyboard_request()
            del self._entries_pressed[widget]

    def on_unfocus_entry(
        self, widget: Gtk.Widget, event: Gdk.EventFocus
    ) -> None:
        """React to an entry being unfocused. Hide the on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        osk_util.unrequest_keyboard()

    def on_opcua_button_clicked(
        self, button: Gtk.Button, category: str, variable_name: str
    ) -> None:
        """React to a button that is represented in OPC UA being clicked.

        Set the boolean OPC UA variable that represents teh button (yuck) to
            True.

        The indended use for this is with a Gtk callback, i.e.:
            button: Gtk.Button
            page: Page
            category: str
            variable_name: str
            ...
            button.connect(
                "clicked", page.on_opcua_button_clicked, category, variable_name
            )

        category and variable_name might look like this:
            Regular way of accessing variable:
                Connection()["main"]["emergency_off_button"]
            Path of variable:
                category: "main"
                variable_name: "emergency_off_button"

        Args:
            button (Gtk.Button): The button that was clicked
            category (str): The name of the NodeCategory that the boolean
                variable (yuck) is in
            variable_name (str): The name of the boolean variable (yuck) node
        """
        Connection()[category][variable_name] = True
