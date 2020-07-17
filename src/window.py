"""The main Liegensteuerung window."""

from typing import Union, Optional, List, Dict, Iterable, Any

from gi.repository import GLib, Gtk  # type: ignore

from . import auth_util
from . import patient_util
from . import page
from . import (
    register_page,
    login_page,
    select_patient_page,
    edit_patient_page,
    pain_evaluation_page,
    set_up_page,
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

        active_user (str, optional): The user that is loghged in or None if no
            user is logged in.
    """

    __gtype_name__ = "LiegensteuerungWindow"

    page_stack: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    header_bar_revealer: Union[
        Gtk.Template.Child, Gtk.Revealer
    ] = Gtk.Template.Child()

    no_patient_info_bar: Union[
        Gtk.Template.Child, Gtk.InfoBar
    ] = Gtk.Template.Child()

    error_bar: Union[
        Gtk.Template.Child, Gtk.InfoBar
    ] = Gtk.Template.Child()
    error_bar_label: Union[
        Gtk.Template.Child, Gtk.Label
    ] = Gtk.Template.Child()

    back_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    back_button_revealer: Union[
        Gtk.Template.Child, Gtk.Revealer
    ] = Gtk.Template.Child()

    patient_button: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()

    patient_button_revealer: Union[
        Gtk.Template.Child, Gtk.Revealer
    ] = Gtk.Template.Child()

    shutdown_button: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()
    log_out_button: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()

    users_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    change_password_button: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()

    title_label: Union[Gtk.Template.Child, Gtk.Label] = Gtk.Template.Child()

    main_area_overlay: Union[
        Gtk.Template.Child, Gtk.Overlay
    ] = Gtk.Template.Child()
    shutdown_button_compact: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()
    shutdown_compact_revealer: Union[
        Gtk.Template.Child, Gtk.Button
    ] = Gtk.Template.Child()

    active_user: Optional[str] = None
    active_user_password: Optional[str] = None
    active_patient: Optional[patient_util.Patient] = None

    page_history: List[str] = []

    def __init__(self, **kwargs):
        """Create a new LiegensteuerungWindow.

        Args:
            **kwargs: Arguments passed on to Gtk.Window
        """
        super().__init__(**kwargs)

        self.maximize()

        if auth_util.does_admin_exist():
            self.switch_page("login")
        else:
            self.switch_page(
                "register",
                new_user=True,
                access_level="admin",
                next_page="select_patient",
            )

        self.connect_after("show", self.on_show)

    def on_show(self, widget) -> None:
        """React to being shown.

        At this point, all Gtk.Template.Child objects should have been replaced
            by actual Gtk.Widgets. Therefore, signals are connected here.
        """
        self.back_button.connect("clicked", self.on_back_clicked)
        self.patient_button.connect("clicked", self.on_patient_clicked)

        self.no_patient_info_bar.connect("response", self.on_info_bar_response)
        self.error_bar.connect("response", self.on_info_bar_response)

        self.main_area_overlay.add_overlay(self.shutdown_compact_revealer)

    def switch_page(self, page_name: str, *args, **kwargs,) -> None:
        """Switch the active page.

        Args:
            page_name (str): The Page to switch to. Names as in window.ui

            *args: Arguments to pass to Page.prepare()
            **kwargs: Keyword arguments to pass to Page.prepare()
        """
        self.page_history.append(page_name)

        self._show_page(
            page_name, animation_direction=1, args=args, kwargs=kwargs
        )

    def go_back(self) -> None:
        """Switch to the last visited Page."""
        self.page_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_RIGHT
        )

        self.page_history.pop()

        self._show_page(
            self.page_history[-1],
            animation_direction=-1,
            prepare=False,
            prepare_return=True,
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
            self.page_stack.set_transition_type(
                Gtk.StackTransitionType.SLIDE_RIGHT
            )
        elif animation_direction == 0:
            self.page_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        elif animation_direction == 1:
            self.page_stack.set_transition_type(
                Gtk.StackTransitionType.SLIDE_LEFT
            )
        else:
            raise ValueError("animation_direction must be -1, 0 or 1")

        next_page: page.Page = self.page_stack.get_child_by_name(page_name)

        if next_page is None:
            raise ValueError(f'"{page_name}" is not a valid Page name')

        if prepare:
            next_page.prepare(*args, **kwargs)
        if prepare_return:
            next_page.prepare_return()

        # Show Page
        self.page_stack.set_visible_child_name(self.page_history[-1])

        # Hide previous errors
        self.error_bar.set_revealed(False)

        # Adapt header bar
        self.header_bar_revealer.set_reveal_child(next_page.header_visible)
        self.shutdown_compact_revealer.set_reveal_child(
            not next_page.header_visible
        )

        self.title_label.set_text(next_page.title)

        # Change button visibility
        self.back_button_revealer.set_reveal_child(len(self.page_history) > 1)

        self.log_out_button.set_visible(self.active_user is not None)

        is_admin: bool = (
            self.active_user is not None
            and auth_util.get_access_level(self.active_user) == "admin"
        )
        self.users_button.set_visible(is_admin)
        self.change_password_button.set_visible(not is_admin)

        self.patient_button_revealer.set_reveal_child(
            self.active_patient is not None
            and not next_page.is_patient_info_page
        )

    def clear_history(self) -> None:
        """Clear the page history."""
        self.page_history = [self.page_stack.get_visible_child_name()]
        self.back_button_revealer.set_reveal_child(len(self.page_history) > 1)

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

    def on_info_bar_response(self, info_bar: Gtk.InfoBar, response: int):
        """React to the user responding to a Gtk.InfoBar.

        Args:
            info_bar (Gtk.InfoBar): The Gtk.InfoBar that received the response
            response (int): The response id (Gtk.ResponseType)
        """
        if response == Gtk.ResponseType.CLOSE:
            info_bar.set_revealed(False)
            GLib.timeout_add(250, info_bar.set_visible, False)
