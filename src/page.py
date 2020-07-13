"""A page that prompts the user to register."""

from gi.repository import GObject, Gdk, Gtk  # type: ignore

from . import onboard_util

import abc


class PageClass(abc.ABCMeta, type(Gtk.Box)):
    pass


class Page(abc.ABC):
    """An abstract page superclass that prompts the user to register.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The page's title
    """

    @property
    @abc.abstractmethod
    def header_visible(self) -> bool:
        """Whether the window header bar should be visible for this page."""
        ...

    @property
    @abc.abstractmethod
    def title(self) -> str:
        """Title of this page shown in the window header bar."""
        ...

    @abc.abstractmethod
    def prepare(
        self
    ) -> None:
        """Prepare the page to be shown.

        This may take any amount of arguments and keyword arguments.
        """
        ...

    def on_focus_entry(
        self, widget: Gtk.Widget, event: Gdk.EventFocus
    ) -> None:
        """React to an entry being focused. Show an on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        onboard_util.request_keyboard()

    def on_unfocus_entry(
        self, widget: Gtk.Widget, event: Gdk.EventFocus
    ) -> None:
        """React to an entry being unfocused. Hide the on-screen keyboard.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        onboard_util.unrequest_keyboard()


if __name__ == '__main__':
    class TestPage(Page):
        title = "TestPage"
        header_visible = False

        def prepare(self):
            pass

    TestPage()
