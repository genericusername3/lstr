"""A page that prompts the user to register."""

from typing import Union, Optional, Iterable, Any, Dict

from gi.repository import GObject, Gtk  # type: ignore

import passwordmeter  # type: ignore

from .page import Page, PageClass

from . import auth_util


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/register_page.ui"
)
class RegisterPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to register.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The page's title
        username_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
        password_entry (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's new password
        password_confirm_entry (Gtk.Entry or Gtk.Template.Child): The entry for
            the user's new password (again, to confirm)
        register_button (Gtk.Button or Gtk.Template.Child): The button that is
            clicked to compolete the register
        next_page (str, optional): Page to switch to when done. None to go back
        next_page_args (Iterable[Any]): Arguments to pass to the next page
            (if next_page isn't None)
        next_page_kwargs (Dict[str, Any]): Keyword arguments to pass to the
            next page (if next_page isn't None)
    """

    __gtype_name__ = "RegisterPage"

    header_visible: bool = False
    title: str = "Registrieren"

    username_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    password_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    password_confirm_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    access_level_combobox: Union[
        Gtk.ComboBoxText, Gtk.Template.Child
    ] = Gtk.Template.Child()

    register_button: Union[
        Gtk.Button, Gtk.Template.Child
    ] = Gtk.Template.Child()
    accept_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    next_page: Optional[str] = None
    next_page_args: Iterable[Any] = ()
    next_page_kwargs: Dict[str, Any] = {}

    username: Optional[str] = None

    def __init__(self, **kwargs):
        """Create a new RegisterPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(
        self,
        new_user: bool = True,
        username: Optional[str] = None,
        access_level: Optional[str] = "user",
        next_page: Optional[str] = None,
        next_page_args: Iterable[Any] = (),
        next_page_kwargs: Dict[str, Any] = {},
    ) -> None:
        """Prepare the page to be shown.

        Args:
            new_user (bool, optional): Whether the RegisterPage is used to
                create a new user (as opposed to changing the password)
            username (Optional[str], optional): The user whose password is
                being changed. Ignored if new_user is True. Defaults to None
            access_level (Optional[str], optional): The default access level
                for a new user. Ignored if new_user is False. See auth_util for
                valid access level names. Defaults to "user"
            next_page (Optional[str], optional): The page to switch to on
                completion. None to go back. Defaults to None
            next_page_args (Iterable[Any], optional): Arguments to pass to the
                next page
            next_page_kwargs (Dict[str, Any], optional): Keyword arguments to
                pass to the next page
        """
        self.username_entry.set_visible(new_user)
        self.username_entry.set_text("")

        self.password_entry.set_text("")
        self.password_confirm_entry.set_text("")

        self.access_level_combobox.set_visible(
            new_user and access_level is None
        )

        if new_user:
            self.access_level_combobox.set_active_id(access_level)
            self.title = "Registrieren"
        else:
            self.title = "Passwort ändern"

        self.register_button.set_visible(new_user)
        self.accept_button.set_visible(not new_user)

        self.next_page = next_page
        self.username = username

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
        self.password_confirm_entry.connect(
            "focus-in-event", self.on_focus_entry
        )

        self.username_entry.connect("focus-out-event", self.on_unfocus_entry)
        self.password_entry.connect("focus-out-event", self.on_unfocus_entry)
        self.password_confirm_entry.connect(
            "focus-out-event", self.on_unfocus_entry
        )

        self.username_entry.connect("changed", self.on_entry_changed)
        self.password_entry.connect("changed", self.on_entry_changed)
        self.password_confirm_entry.connect("changed", self.on_entry_changed)

        self.register_button.connect("clicked", self.on_register_clicked)

    def on_entry_changed(self, entry: Gtk.Entry) -> None:
        """React to an entry being changed.

        Removes the 'error' CSS class from the entry.

        Args:
            entry (Gtk.Entry): The changed entry
        """
        if entry is self.password_entry:
            entry.get_style_context().remove_class("error")

            if entry.get_text() == self.password_confirm_entry.get_text():
                self.password_confirm_entry.get_style_context().remove_class(
                    "error"
                )

            if entry.get_text() == "":
                entry.set_progress_fraction(0)
            else:
                strength, improvements = passwordmeter.test(entry.get_text())
                entry.set_progress_fraction(strength)

                if strength > 2 / 3.0:
                    entry.get_style_context().remove_class("bad")
                    entry.get_style_context().remove_class("medium")
                    entry.get_style_context().add_class("good")
                elif strength > 1 / 3.0:
                    entry.get_style_context().remove_class("bad")
                    entry.get_style_context().add_class("medium")
                    entry.get_style_context().remove_class("good")
                else:
                    entry.get_style_context().add_class("bad")
                    entry.get_style_context().remove_class("medium")
                    entry.get_style_context().remove_class("good")

        elif entry is self.password_confirm_entry:
            if entry.get_text() == self.password_entry.get_text():
                entry.get_style_context().remove_class("error")
            else:
                entry.get_style_context().add_class("error")

        elif entry is self.username_entry:
            entry.get_style_context().remove_class("error")

    def on_register_clicked(self, button: Gtk.Button) -> None:
        """React to the register button being clicked.

        Args:
            button (Gtk.Button): The register button
        """
        for entry in (
            self.username_entry,
            self.password_entry,
            self.password_confirm_entry,
        ):
            if entry.get_text() == "":
                entry.grab_focus()
                entry.get_style_context().add_class("error")
                return

        if (
            self.password_entry.get_text()
            != self.password_confirm_entry.get_text()
        ):
            self.password_confirm_entry.grab_focus()
            self.password_confirm_entry.get_style_context().add_class("error")
            return

        try:
            auth_util.new_user(
                self.username_entry.get_text(),
                self.password_entry.get_text(),
                self.access_level_combobox.get_active_id(),
                self.get_toplevel().active_user,
                self.get_toplevel().active_user_password,
            )

            if self.next_page is None:
                self.get_toplevel().go_back()
            else:
                self.get_toplevel().switch_page(
                    self.next_page,
                    *self.next_page_args,
                    **self.next_page_kwargs
                )

            if self.get_toplevel().active_user is None:
                self.get_toplevel().active_user = (
                    self.username_entry.get_text()
                )
                self.get_toplevel().active_user_password = (
                    self.password_entry.get_text()
                )

                self.get_toplevel().clear_history()

        except ValueError as v_err:
            self.get_toplevel().show_error(" ".join(v_err.args))

    def on_accept_clicked(self, button: Gtk.Button) -> None:
        """React to the accept button being clicked.

        Args:
            button (Gtk.Button): The accept button
        """
        try:
            for entry in (
                self.password_entry,
                self.password_confirm_entry,
            ):
                if entry.get_text() == "":
                    entry.grab_focus()
                    entry.get_style_context().add_class("error")
                    return

            if (
                self.password_entry.get_text()
                != self.password_confirm_entry.get_text()
            ):
                self.password_confirm_entry.grab_focus()
                self.password_confirm_entry.get_style_context().add_class(
                    "error"
                )
                return

            if (
                self.username is not None
                and self.get_toplevel().active_user is not None
            ):
                if self.get_toplevel().active_user == self.username:
                    auth_util.modify_password(
                        self.username,
                        self.get_toplevel().active_user_password,
                        self.password_entry.get_text(),
                    )
                elif (
                    auth_util.get_access_level(self.get_toplevel().active_user)
                    == "admin"
                ):
                    auth_util.modify_password_from_admin(
                        self.username,
                        self.password_entry.get_text(),
                        self.get_toplevel().active_user,
                        self.get_toplevel().active_user_password,
                    )
                else:
                    auth_util.modify_password(
                        self.get_toplevel().active_user,
                        self.get_toplevel().active_user_password,
                        self.password_entry.get_text(),
                    )
            else:
                raise ValueError(
                    "A user must be logged in to change a password"
                )

            if self.next_page is None:
                self.get_toplevel().go_back()
            else:
                self.get_toplevel().switch_page(
                    self.next_page,
                    *self.next_page_args,
                    **self.next_page_kwargs
                )

        except ValueError as v_err:
            self.get_toplevel().show_error(" ".join(v_err.args))


# Make RegisterPage accessible via .ui files
GObject.type_ensure(RegisterPage)
