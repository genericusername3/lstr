"""The main Liegensteuerung window."""

from typing import Union, Optional, List, Dict, Iterable, Any

import subprocess

from gi.repository import GLib, Gtk  # type: ignore

from . import auth_util
from . import patient_util
from . import program_util
from . import osk_util
from . import page
from . import (
    keyboard,
    calibration_page,
    edit_patient_page,
    edit_program_page,
    login_page,
    pain_evaluation_page,
    register_page,
    select_patient_page,
    select_program_page,
    set_up_page,
    treatment_page,
    users_page,
)


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/window.ui")
class LiegensteuerungWindow(Gtk.ApplicationWindow):
    """
    The main Liegensteuerung window.

    Attributes:
        page_stack (Union[Gtk.Template.Child, Gtk.Stack]): The Gtk.Stack
            containing all pages.
        header_bar_revealer (Union[Gtk.Template.Child, Gtk.Revealer]): A
            Gtk.Revealer that contains the header bar.

        error_bar (Union[Gtk.Template.Child, Gtk.MessageBar]): A Gtk.Message
            bar used to inform the user about occurring errors
        error_bar_label (Union[Gtk.Template.Child, Gtk.Label]): The Gtk.Label
            that contains the error message of self.error_bar

        back_button (Union[Gtk.Template.Child, Gtk.Button]): A button that
            offers the user to go back to the previous page
        back_button_revealer (Union[Gtk.Template.Child, Gtk.Revealer]): A
            Gtk.Revealer that reveals self.back_button based on whether going
            back is possible (history length > 1)

        patient_button (Union[Gtk.Template.Child, Gtk.Button]): A button that
            offers the user to view and edit the active patient
        patient_button_revealer (Union[Gtk.Template.Child, Gtk.Revealer]): A
            Gtk.Revealer that reveals self.patient_button based on whether a
            patient is selected (self.active_patient is not None)

        shutdown_button (Union[Gtk.Template.Child, Gtk.Button]): A button that
            offers the user to shut down
        log_out_button (Union[Gtk.Template.Child, Gtk.Button]): A button that
            offers the user to log out

        users_button (Union[Gtk.Template.Child, Gtk.Button]): A button that
            offers an administrator or doctor to view and edit users with lower
            access levels
        change_password_button (Union[Gtk.Template.Child, Gtk.Button]): A
            button that offers the user to change their own password

        title_label (Union[Gtk.Template.Child, Gtk.Label]): A label that
            displays the title of the active page

        main_area_overlay (Union[Gtk.Template.Child, Gtk.Overlay]): A
            Gtk.Overlay over the Gtk.Stack that displays the pages
        shutdown_button_compact (Union[Gtk.Template.Child, Gtk.Button]): A
            button that offers the user to shut down on pages that do not
            display the title bar
        shutdown_compact_revealer (Union[Gtk.Template.Child, Gtk.Revealer]): A
            Gtk.Revealer that reveals self.shutdown_button_compact based on
            whether the title bar is shown

        active_user (str, optional): The user that is logged in or None if no
            user is logged in.
        active_user_password (str, optional): The active user's password
        active_patient (patient_util.Patient, optional): The selected patient
            or None
        active_program (program_util.Program, optional): The selected program
            or None

        page_history (List[str]): A list of previous page IDs that the user can
            go back to
    """

    __gtype_name__ = "LiegensteuerungWindow"

    page_stack: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    header_bar_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()

    error_bar: Union[Gtk.Template.Child, Gtk.InfoBar] = Gtk.Template.Child()
    error_bar_label: Union[Gtk.Template.Child, Gtk.Label] = Gtk.Template.Child()

    back_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    back_button_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()

    more_popover: Union[Gtk.Template.Child, Gtk.Popover] = Gtk.Template.Child()

    patient_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    patient_button_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()

    shutdown_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    log_out_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    log_out_button_compact: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()

    users_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    change_password_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()

    title_label: Union[Gtk.Template.Child, Gtk.Label] = Gtk.Template.Child()

    main_area_overlay: Union[Gtk.Template.Child, Gtk.Overlay] = Gtk.Template.Child()
    shutdown_button_compact: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    shutdown_compact_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()
    log_out_compact_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()

    keyboard_revealer: Union[Gtk.Template.Child, Gtk.Revealer] = Gtk.Template.Child()

    active_user: Optional[str] = None
    active_user_password: Optional[str] = None
    active_patient: Optional[patient_util.Patient] = None
    active_program: Optional[program_util.Program] = None

    page_history: List[str] = []

    def __init__(self, **kwargs):
        """Create a new LiegensteuerungWindow.

        Args:
            **kwargs: Arguments passed on to Gtk.Window
        """
        super().__init__(**kwargs)

        self.maximize()
        self.set_decorated(False)

        self.connect_after("show", self.on_show)

        self.log_out()

    def on_show(self, widget) -> None:
        """React to being shown.

        At this point, all Gtk.Template.Child objects should have been replaced
            by actual Gtk.Widgets. Therefore, signals are connected here.
        """
        osk_util.set_keyboard(self.keyboard_revealer)

        self.back_button.connect("clicked", self.on_back_clicked)
        self.patient_button.connect("clicked", self.on_patient_clicked)

        self.error_bar.connect("response", self.on_info_bar_response)

        self.main_area_overlay.add_overlay(self.shutdown_compact_revealer)

        self.change_password_button.connect("clicked", self.on_change_password_clicked)
        self.users_button.connect("clicked", self.on_users_clicked)

        self.log_out_button.connect("clicked", self.on_log_out_clicked)
        self.log_out_button_compact.connect("clicked", self.on_log_out_clicked)

        self.shutdown_button.connect("clicked", self.on_shutdown_clicked)
        self.shutdown_button_compact.connect("clicked", self.on_shutdown_clicked)

    def log_out(self) -> None:
        """Log out and go to the log in or register page."""
        if not auth_util.does_admin_exist():
            self._show_page(
                "register",
                animation_direction=-1,
                kwargs={"new_user": True, "access_level": "admin", "next_page": "calibration",},
            )
        elif not auth_util.does_doctor_exist():
            self._show_page(
                "register",
                animation_direction=-1,
                kwargs={"new_user": True, "access_level": "doctor", "next_page": "calibration",},
            )
        else:
            self._show_page("login", animation_direction=-1)

        self.clear_history()

    def switch_page(self, page_name: str, *args, **kwargs,) -> None:
        """Switch the active page.

        Args:
            page_name (str): The Page to switch to. Names as in window.ui

            *args: Arguments to pass to Page.prepare()
            **kwargs: Keyword arguments to pass to Page.prepare()
        """
        self.page_history.append(page_name)

        self._show_page(page_name, animation_direction=1, args=args, kwargs=kwargs)

    def go_back(self) -> None:
        """Switch to the last visited Page."""
        self.page_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)

        self.page_history.pop()

        self._show_page(
            self.page_history[-1], animation_direction=-1, prepare=False, prepare_return=True,
        )

    def _show_page(
        self,
        page_name: str,
        animation_direction: int = 1,
        prepare: bool = True,
        prepare_return: bool = False,
        args: Iterable[Any] = [],
        kwargs: Dict[str, Any] = {},
    ) -> None:
        """Show a Page and adapt the header bar.

        This will not do any history operations

        Args:
            page_name (str): The Page to switch to. Names as in window.ui
            animation_dir (int, optional): -1 for slide to right,
                0 for none, 1 for slide to left
                Defaults to 1
            prepare (bool, optional): Whether to call Page.prepare(). Defaults
                to True
            args (Iterable[Any], optional): Arguments to pass to Page.prepare()
            kwargs (Dict[str, Any], optional): Keyword arguments to pass to
                Page.prepare()
        """
        self.page_stack.get_visible_child().unprepare()

        if animation_direction == -1:
            self.page_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        elif animation_direction == 0:
            self.page_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        elif animation_direction == 1:
            self.page_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        else:
            raise ValueError("animation_direction must be -1, 0 or 1")

        next_page: page.Page = self.page_stack.get_child_by_name(page_name)

        if next_page is None:
            raise ValueError(f'"{page_name}" is not a valid Page name')

        # Hide previous errors
        self.error_bar.set_revealed(False)
        self.error_bar.set_visible(False)

        if prepare:
            relay_page = next_page.prepare(*args, **kwargs)
        if prepare_return:
            relay_page = next_page.prepare_return()

        if isinstance(relay_page, str):
            if len(self.page_history) and self.page_history[-1] == page_name:
                self.page_history.pop()

            return self._show_page(page_name=relay_page, animation_direction=animation_direction,)

        elif isinstance(relay_page, tuple):
            if len(self.page_history) and self.page_history[-1] == page_name:
                self.page_history.pop()

            return self._show_page(*relay_page)

        # Show Page
        self.page_stack.set_visible_child_name(page_name)

        # Adapt header bar
        self.header_bar_revealer.set_reveal_child(next_page.header_visible)
        self.shutdown_compact_revealer.set_reveal_child(not next_page.header_visible)

        self.update_title()

        # Change button visibility
        self.back_button_revealer.set_reveal_child(len(self.page_history) > 1)

        self.log_out_button.set_visible(self.active_user is not None)
        self.log_out_compact_revealer.set_reveal_child(self.active_user is not None)

        is_admin: bool = (
            self.active_user is not None and auth_util.get_access_level(self.active_user) == "admin"
        )
        is_doctor: bool = (
            self.active_user is not None
            and auth_util.get_access_level(self.active_user) == "doctor"
        )
        self.users_button.set_visible(is_admin or is_doctor)

        self.patient_button_revealer.set_reveal_child(
            self.active_patient is not None and not next_page.is_patient_info_page
        )

    def clear_history(self) -> None:
        """Clear the page history."""
        self.page_history = [self.page_stack.get_visible_child_name()]
        self.back_button_revealer.set_reveal_child(len(self.page_history) > 1)

    def update_title(self) -> None:
        """Update the displayed title according to the current page's title."""
        self.title_label.set_text(self.page_stack.get_visible_child().title)

    def show_error(self, message: str) -> None:
        """Show an error message to the user.

        Args:
            message (str): The message to show
        """
        self.error_bar_label.set_text(message)

        self.error_bar.set_visible(True)
        self.error_bar.set_revealed(True)

    def on_back_clicked(self, button: Gtk.Button) -> None:
        """React to the back button being clicked. Go back.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.go_back()

    def on_patient_clicked(self, button: Gtk.Button) -> None:
        """React to the "Patient..." button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.switch_page("edit_patient", patient=self.active_patient)

    def on_change_password_clicked(self, button: Gtk.Button) -> None:
        """React to the "Change password" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.more_popover.popdown()

        assert self.active_user is not None

        self.switch_page(
            "register",
            new_user=False,
            username=self.active_user,
            access_level=auth_util.get_access_level(self.active_user),
        )

    def on_users_clicked(self, button: Gtk.Button) -> None:
        """React to the "Users..." button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.more_popover.popdown()

        self.switch_page("users")

    def on_log_out_clicked(self, button: Gtk.Button) -> None:
        """React to the "Log out" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.more_popover.popdown()
        self.log_out()

    def on_shutdown_clicked(self, button: Gtk.Button) -> None:
        """React to the "Shutdown" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        print("Presenting shutdown dialog")

        self.more_popover.popdown()

        self.get_style_context().add_class("has-dialog")

        dialog = Gtk.MessageDialog(
            self.get_toplevel(),
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            ("Nein", Gtk.ResponseType.NO, "Ja", Gtk.ResponseType.YES),
            (f"Jetzt herunterfahren?"),
        )
        dialog.set_decorated(False)
        response: int = dialog.run()
        dialog.destroy()

        self.get_style_context().remove_class("has-dialog")

        if response == Gtk.ResponseType.YES:
            subprocess.call(("shutdown", "-h", "now"))

        elif response == Gtk.ResponseType.NO:
            pass

    def on_info_bar_response(self, info_bar: Gtk.InfoBar, response: int):
        """React to the user responding to a Gtk.InfoBar.

        Args:
            info_bar (Gtk.InfoBar): The Gtk.InfoBar that received the response
            response (int): The response id (Gtk.ResponseType)
        """
        if response == Gtk.ResponseType.CLOSE:
            info_bar.set_revealed(False)
            GLib.timeout_add(250, info_bar.set_visible, False)
