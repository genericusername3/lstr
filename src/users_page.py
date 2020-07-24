"""A page that prompts the user manage all existent users."""

from typing import Union, Optional, List

from gi.repository import GObject, Gio, Gtk  # type: ignore

from .page import Page, PageClass

from .user_row import UserRow, UserHeader
from .user_util import User

from . import auth_util


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/users_page.ui")
class UsersPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user manage all existent users.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        user_list_box (Gtk.ListBox or Gtk.Template.Child): The listbox
            displaying users
    """

    __gtype_name__ = "UsersPage"

    header_visible: bool = True
    title: str = "Benutzer"

    user_list_box: Union[
        Gtk.ListBox, Gtk.Template.Child
    ] = Gtk.Template.Child()

    header_box: Union[Gtk.Box, Gtk.Template.Child] = Gtk.Template.Child()

    add_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new SelectUserPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        self.update_users()

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        # Inefficient to re-load all users, but everything else is more work
        self.update_users()

    def update_users(self) -> None:
        """Re-query all users."""
        self.user_list_box.bind_model(
            User.iter_to_model(User.get_all()),
            UserRow,
            self.get_toplevel().active_user,
            self,
        )
        self.user_list_box.show_all()

        for row in self.user_list_box.get_children():
            row.set_activatable(False)

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.header_box.pack_start(
            UserHeader(), fill=True, expand=True, padding=0
        )
        self.header_box.show_all()

        self.add_button.connect("clicked", self.on_add_clicked)

    def on_add_clicked(self, button: Gtk.Button) -> None:
        """React to the "Add user" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page(
            "register",
            new_user=True,
            # Hardcoded access level because that hopefully
            # isn't changing anytime soon
            access_level="helper",
        )


# Make UsersPage accessible via .ui files
GObject.type_ensure(UsersPage)
