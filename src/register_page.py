"""A page that prompts the user to log in."""

from typing import Union, Optional

from gi.repository import GObject, Gdk, Gtk  # type: ignore

from . import onboard_util
from . import auth_util


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/login_page.ui")
class LoginPage(Gtk.Box):
    """A page that prompts the user to log in.

    Attributes:
        username_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
        password_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's password
        log_in_button (Gtk.Button or Gtk.Template.Child): The button that is
            clicked to compolete the log-in
    """

    __gtype_name__ = "LoginPage"

    username_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    password_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    log_in_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new LoginPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.username_entry.connect("focus-in-event", self.on_focus_entry)
        self.password_entry.connect("focus-in-event", self.on_focus_entry)

        self.username_entry.connect("focus-out-event", self.on_unfocus_entry)
        self.password_entry.connect("focus-out-event", self.on_unfocus_entry)

        self.username_entry.connect("changed", self.on_entry_changed)
        self.password_entry.connect("changed", self.on_entry_changed)

        self.log_in_button.connect("clicked", self.on_log_in_clicked)

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

    def on_entry_changed(self, entry: Gtk.Entry) -> None:
        entry.get_style_context().remove_class("error")

    def on_log_in_clicked(self, button: Gtk.Button) -> None:
        """React to the log in button being clicked.

        Args:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        try:
            if auth_util.authenticate(
                self.username_entry.get_text(), self.password_entry.get_text()
            ):
                onboard_util.unrequest_keyboard()
                print("LOGGED IN")
                ...

            else:
                self.password_entry.get_style_context().add_class("error")
                self.password_entry.grab_focus_without_selecting()
        except ValueError as e:
            print(e)
            self.username_entry.get_style_context().add_class("error")
            self.username_entry.grab_focus_without_selecting()


# Make LoginPage accessible via .ui files
GObject.type_ensure(LoginPage)
