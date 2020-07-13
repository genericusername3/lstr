"""The main Liegensteuerung window."""

from typing import Union, Optional, List

from gi.repository import Gtk  # type: ignore

from . import auth_util
from . import page
from . import (
    register_page,
    login_page,
    select_patient_page,
    edit_patient_page,
    set_up_page,
)


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/window.ui")
class LiegensteuerungWindow(Gtk.ApplicationWindow):
    """
    The main Liegensteuerung window.

    Attributes:
        page_stack (Union[Gtk.Template.Child, Gtk.Stack]): The Gtk.Stack
            containing all pages.
        header_bar_revealer (Union[Gtk.Template.Child, Gtk.Stack]): The Gtk.Stack
            containing all pages.

        active_user (str, optional): The user that is loghged in or None if no
            user is logged in.
    """

    __gtype_name__ = "LiegensteuerungWindow"

    page_stack: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    header_bar_revealer: Union[
        Gtk.Template.Child, Gtk.Revealer
    ] = Gtk.Template.Child()

    back_button: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    patient_button: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    shutdown_button: Union[
        Gtk.Template.Child, Gtk.Stack
    ] = Gtk.Template.Child()
    log_out_button: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()

    users_button: Union[Gtk.Template.Child, Gtk.Stack] = Gtk.Template.Child()
    change_password_button: Union[
        Gtk.Template.Child, Gtk.Stack
    ] = Gtk.Template.Child()

    active_user: Optional[str] = None
    active_user_password: Optional[str] = None

    page_history: List[str] = []

    def __init__(self, **kwargs):
        """Create a new LiegensteuerungWindow.

        Args:
            **kwargs: Arguments passed on to Gtk.Window
        """
        super().__init__(**kwargs)

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
        """
        React to being shown.

        At this point, all Gtk.Template.Child objects should have been replaced
            by actual Gtk.Widgets. Therefore, signals are connected here.
        """
        self.back_button.connect("clicked", self.on_back_button_clicked)

    def switch_page(
        self,
        page_name: str,
        animation_dir: Optional[int] = 1,
        *args,
        **kwargs,
    ) -> None:
        """Switch the active page.

        Args:
            page_name (str): The page to switch to. Names as in window.ui
            animation_dir (int, optional): -1 for slide to right,
                0 for default, 1 for slide to left, None for none.
                Defaults to 1

            *args: Arguments to pass to the page
            **kwargs: Keyword arguments to pass to the page
        """
        # TODO: Set animation direction

        page = self.page_stack.get_child_by_name(page_name)
        page.prepare(*args, **kwargs)
        self.header_bar_revealer.set_reveal_child(page.header_visible)

        self.page_stack.set_visible_child_name(page_name)

        self.page_history.append(page_name)

        if len(self.page_history) >= 1:
            self.back_button.show()

    def go_back(self) -> None:
        """Switch the active page to the last visited page."""
        self.page_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_RIGHT
        )

        self.page_history.pop()

        self.page_stack.set_visible_child_name(self.page_history[-1])

        if len(self.page_history) <= 1:
            self.back_button.hide()

    def clear_history(self) -> None:
        """Clear the page history."""
        self.page_history = [self.page_stack.get_visible_child_name()]
        self.back_button.hide()

    def on_back_button_clicked(self, button: Gtk.Button) -> None:
        """React to the back button being clicked. Go back.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.go_back()
