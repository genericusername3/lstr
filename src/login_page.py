"""A page that prompts the user to log in.
"""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from . import auth_util


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/login_page.ui")
class LoginPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to log in.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The page's title
        username_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
        password_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's password
        log_in_button (Gtk.Button or Gtk.Template.Child): The button that is
            clicked to compolete the log-in
    """

    __gtype_name__ = "LoginPage"

    header_visible: bool = False
    title: str = "Anmelden"

    username_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    password_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    log_in_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new LoginPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        self.get_toplevel().active_user = None

        self.username_entry.set_text("")
        self.password_entry.set_text("")

        self.username_entry.grab_focus()

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent

        Returns:
            None: Description
        """
        if self.get_parent() is None:
            return

        self.username_entry.connect("focus-in-event", self.on_focus_entry)
        self.password_entry.connect("focus-in-event", self.on_focus_entry)

        self.username_entry.connect("focus-out-event", self.on_unfocus_entry)
        self.password_entry.connect("focus-out-event", self.on_unfocus_entry)

        self.username_entry.connect("button-press-event", self.on_entry_button_press)
        self.password_entry.connect("button-press-event", self.on_entry_button_press)

        self.username_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.password_entry.connect(
            "button-release-event", self.on_entry_button_release
        )

        self.username_entry.connect("changed", self.on_entry_changed)
        self.password_entry.connect("changed", self.on_entry_changed)

        self.log_in_button.connect("clicked", self.on_log_in_clicked)

    def on_entry_changed(self, entry: Gtk.Entry) -> None:
        """React to the text of an entry changing. Removes the 'error' CSS
            class from the entry.

        Args:
            entry (Gtk.Entry): The changed entry
        """
        entry.get_style_context().remove_class("error")

    def on_log_in_clicked(self, button: Gtk.Button) -> None:
        """React to the log in button being clicked.

        Args:
            button (Gtk.Button): Description

        Deleted Parameters:
            widget (Gtk.Widget): The focused entry.
            event (Gdk.EventFocus): The focus event.
        """
        try:
            if auth_util.authenticate(
                self.username_entry.get_text(), self.password_entry.get_text()
            ):
                self.get_toplevel().active_user = self.username_entry.get_text()
                self.get_toplevel().active_user_password = (
                    self.password_entry.get_text()
                )

                self.get_toplevel().switch_page("calibration")

                self.get_toplevel().clear_history()

            else:
                self.password_entry.get_style_context().add_class("error")
                self.password_entry.grab_focus_without_selecting()
        except ValueError as e:
            print(e)
            self.username_entry.get_style_context().add_class("error")
            self.username_entry.grab_focus_without_selecting()


# Make LoginPage accessible via .ui files
GObject.type_ensure(LoginPage)
