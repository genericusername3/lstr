"""A page that prompts the user to register."""

from typing import Dict, Optional, Tuple, Iterable, Any, overload

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

    @overload
    def prepare(self, *args, **kwargs) -> None:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> str:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> Tuple[str]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            Tuple[str]: The name of the page to relay to (in a tuple)
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> Tuple[str, int]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
            int: The animation direction
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> Tuple[str, int, bool]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> Tuple[str, int, bool, bool]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
        """
        pass

    @overload
    def prepare(self, *args, **kwargs) -> Tuple[str, int, bool, bool, Iterable[Any]]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
            Iterable[Any]: Arguments passed to the relayed page
        """
        pass

    def prepare(
        self, *args, **kwargs
    ) -> Tuple[str, int, bool, bool, Iterable[Any], Dict[str, Any]]:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.

        Args:
            *args: Arguments that the overriding method may take
            **kwargs: Keyword arguments that the overriding method may take

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
            Iterable[Any]: Arguments passed to the relayed page
            Dict[str, Any]: Keyword arguments passed to the relayed page
        """
        pass

    def unprepare(self) -> None:
        """Prepare the page to be hidden."""
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> None:
        """Prepare the page to be shown when returning from another page."""
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> str:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
        """
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> Tuple[str]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            Tuple[str]: The name of the page to relay to in a tuple
        """
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> Tuple[str, int]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
            int: The animation direction
        """
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> Tuple[str, int, bool]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
        """
        pass

    @overload
    def prepare_return(self, *args, **kwargs) -> Tuple[str, int, bool, bool]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
        """
        pass

    @overload
    def prepare_return(
        self, *args, **kwargs
    ) -> Tuple[str, int, bool, bool, Iterable[Any]]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
            Iterable[Any]: Arguments passed to the relayed page
        """
        pass

    def prepare_return(
        self,
    ) -> Tuple[str, int, bool, bool, Iterable[Any], Dict[str, Any]]:
        """Prepare the page to be shown when returning from another page.

        Returns:
            str: The name of the page to relay to
            int: The animation direction
            bool: Whether to prepare the relayed page
            bool: Whether to prepare_return the relayed page
            Iterable[Any]: Arguments passed to the relayed page
            Dict[str, Any]: Keyword arguments passed to the relayed page
        """
        pass

    def on_focus_entry(self, widget: Gtk.Widget, event: Gdk.EventFocus) -> None:
        """React to an entry being focused. Show an on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        osk_util.request_keyboard()

    def on_entry_button_press(self, widget: Gtk.Widget, event: Gdk.EventButton) -> None:
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

    def on_unfocus_entry(self, widget: Gtk.Widget, event: Gdk.EventFocus) -> None:
        """React to an entry being unfocused. Hide the on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        osk_util.unrequest_keyboard()

    def on_opcua_button_pressed(
        self,
        button: Gtk.Button,
        event: Gdk.EventButton,
        category: str,
        variable_name: str,
    ) -> None:
        """React to a button that is represented in OPC UA being pressed.

        Set the boolean OPC UA variable that represents teh button (yuck) to
            True.

        The indended use for this is with a Gtk callback, i.e.:
            button: Gtk.Button
            page: Page
            category: str
            variable_name: str
            ...

            button.connect(
                "button-press-event",
                page.on_opcua_button_pressed,
                category,
                variable_name,
            )
            button.connect(
                "button-release-event",
                page.on_opcua_button_released,
                category,
                variable_name,
            )


        category and variable_name might look like this:
            Regular way of accessing variable:
                Connection()["main"]["emergency_off_button"]
            Path of variable:
                category: "main"
                variable_name: "emergency_off_button"

        Args:
            button (Gtk.Button): The button that was clicked
            event (Gdk.EventButton): The button event
            category (str): The name of the NodeCategory that the boolean
                variable (yuck) is in
            variable_name (str): The name of the boolean variable (yuck) node
        """
        try:
            Connection()[category][variable_name] = True
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

    def on_opcua_button_released(
        self,
        button: Gtk.Button,
        event: Gdk.EventButton,
        category: str,
        variable_name: str,
    ) -> None:
        """React to a button that is represented in OPC UA being released.

        See on_opcua_button_pressed()

        Args:
            button (Gtk.Button): The button that was clicked
            event (Gdk.EventButton): The button event
            category (str): The name of the NodeCategory that the boolean
                variable (yuck) is in
            variable_name (str): The name of the boolean variable (yuck) node
        """
        try:
            Connection()[category][variable_name] = False
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")
