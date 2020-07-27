"""A widget that represents one user in horizontal orientation.

Ideal for viewing users in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, Union

from gi.repository import GLib, Gtk  # type: ignore

from .page import Page

from . import auth_util
from . import user_util


size_groups: Dict[str, Gtk.SizeGroup] = {}

COLUMN_HEADER_TRANSLATIONS: Dict[str, str] = {
    "username": "Benutzername",
    "access_level": "Zugriffslevel",
}

PASSWORD_ICON = "dialog-password-symbolic"
DELETE_ICON = "user-trash-full-symbolic"


class UserRow(Gtk.Box):
    """A widget that represents one user in horizontal orientation.

    Ideal for viewing users in lists, because all columns are added to a
        Gtk.SizeGroup

    This widget contains a button that offers the user to view more information
        about the user and edit user data.
    """

    user: user_util.User

    def __init__(self, user: user_util.User, username: str, page: Page):
        """Create a new UserRow.

        Args:
            user (user_util.User): The user to represent
            username (str): The username of the current user
            page (Page): The page the UserRow is going to appear on.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.user = user
        self.page = page

        self.access_level: int = auth_util.ACCESS_LEVELS[
            auth_util.get_access_level(username)
        ]
        self.active_user: str = username

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.pack_start(h_box, expand=True, fill=True, padding=0)

        self.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            expand=True,
            fill=True,
            padding=0,
        )

        for column in user_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = GLib.markup_escape_text(str(user.__dict__.get(column)))

            if column == "access_level":
                text = auth_util.ACCESS_LEVEL_TRANSLATIONS[text]

            cell_label = Gtk.Label(label=text)

            cell_label.set_size_request(-1, 32)
            cell_label.set_halign(Gtk.Align.START)
            cell_label.set_margin_start(4)
            cell_label.set_xalign(0)

            size_groups[column].add_widget(cell_label)

            h_box.pack_start(cell_label, expand=True, fill=True, padding=4)

            h_box.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                expand=False,
                fill=False,
                padding=4,
            )

        # Whether the active user can edit the user this row represents
        self.can_edit: bool = (
            self.access_level > auth_util.ACCESS_LEVELS[self.user.access_level]
            or self.active_user == self.user.username
        )

        # Password button
        if size_groups.get("PASSWORD_BUTTON", None) is None:
            size_groups["PASSWORD_BUTTON"] = Gtk.SizeGroup(
                Gtk.SizeGroupMode.BOTH
            )

        change_password_button: Union[Gtk.Button, Gtk.Box]

        if self.can_edit:
            change_password_button = Gtk.Button.new_from_icon_name(
                PASSWORD_ICON, Gtk.IconSize.BUTTON
            )
            change_password_button.set_label("Passwort ändern")
            change_password_button.set_always_show_image(True)
            change_password_button.connect(
                "clicked", self.on_change_password_clicked
            )
        else:
            change_password_button = Gtk.Box()

        change_password_button.set_size_request(48, 48)
        change_password_button.set_margin_top(2)
        change_password_button.set_margin_bottom(2)

        size_groups["PASSWORD_BUTTON"].add_widget(change_password_button)

        h_box.pack_start(
            change_password_button, expand=False, fill=False, padding=4
        )

        # Delete button
        if size_groups.get("DELETE_BUTTON", None) is None:
            size_groups["DELETE_BUTTON"] = Gtk.SizeGroup(
                Gtk.SizeGroupMode.BOTH
            )

        delete_button: Union[Gtk.Button, Gtk.Box]

        if self.can_edit:
            delete_button = Gtk.Button.new_from_icon_name(
                DELETE_ICON, Gtk.IconSize.BUTTON
            )
            delete_button.connect("clicked", self.on_delete_clicked)
        else:
            delete_button = Gtk.Box()

        delete_button.set_size_request(48, 48)
        delete_button.set_margin_top(2)
        delete_button.set_margin_bottom(2)

        size_groups["DELETE_BUTTON"].add_widget(delete_button)

        h_box.pack_start(delete_button, expand=False, fill=False, padding=4)

        self.show_all()

    def on_change_password_clicked(self, button: Gtk.Button) -> None:
        """React to the row's "Change password" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page(
            "register", new_user=False, username=self.user.username,
        )

    def on_delete_clicked(self, button: Gtk.Button) -> None:
        """React to the row's delete button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        dialog = Gtk.MessageDialog(
            self.get_toplevel(),
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            ("Nein", Gtk.ResponseType.NO, "Ja", Gtk.ResponseType.YES),
            (f"Benutzer {self.user.username} unwiderruflich löschen?"),
        )
        dialog.set_decorated(False)
        response: int = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            auth_util.delete_user(
                self.user.username,
                self.active_user,
                self.get_toplevel().active_user_password,
            )
            if self.active_user == self.user.username:
                self.get_toplevel().log_out()
            else:
                self.page.prepare()

        elif response == Gtk.ResponseType.NO:
            pass


class UserHeader(Gtk.Box):
    """A widget that acts as a header for UserRow widgets."""

    def __init__(self):
        """Create a new UserHeader."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_margin_start(2)
        self.set_margin_end(2)

        for column in user_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = COLUMN_HEADER_TRANSLATIONS[column]

            cell_label = Gtk.Label(label=text)

            cell_label.set_size_request(-1, 32)
            cell_label.set_halign(Gtk.Align.START)
            cell_label.set_margin_start(4)
            cell_label.set_xalign(0)

            size_groups[column].add_widget(cell_label)

            self.pack_start(cell_label, expand=True, fill=True, padding=4)

            self.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                expand=False,
                fill=False,
                padding=4,
            )

        # Password button
        if size_groups.get("PASSWORD_BUTTON", None) is None:
            size_groups["PASSWORD_BUTTON"] = Gtk.SizeGroup(
                Gtk.SizeGroupMode.BOTH
            )

        password_button_dummy: Gtk.Button = Gtk.Box()
        password_button_dummy.set_size_request(40, 40)
        password_button_dummy.set_margin_top(2)
        password_button_dummy.set_margin_bottom(2)

        size_groups["PASSWORD_BUTTON"].add_widget(password_button_dummy)

        self.pack_start(
            password_button_dummy, expand=False, fill=False, padding=4
        )

        # Delete button
        if size_groups.get("DELETE_BUTTON", None) is None:
            size_groups["DELETE_BUTTON"] = Gtk.SizeGroup(
                Gtk.SizeGroupMode.BOTH
            )

        delete_button_dummy: Gtk.Button = Gtk.Box()
        delete_button_dummy.set_size_request(40, 40)
        delete_button_dummy.set_margin_top(2)
        delete_button_dummy.set_margin_bottom(2)

        size_groups["DELETE_BUTTON"].add_widget(delete_button_dummy)

        self.pack_start(
            delete_button_dummy, expand=False, fill=False, padding=4
        )

        self.show_all()
