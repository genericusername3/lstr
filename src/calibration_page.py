"""A page that prompts the user to input the patient's pain values."""

from typing import Union, Optional, List, Tuple, Callable, Any

from gi.repository import GObject, GLib, Gtk  # type: ignore

from .page import Page, PageClass

from . import opcua_util
from . import const


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/calibration_page.ui")
class CalibrationPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that waits for user input to calibrate the motors.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        calibrate_button (Gtk.Button or Gtk.Template.Child): The button that starts the calibration
    """

    __gtype_name__ = "CalibrationPage"

    header_visible: bool = False
    title: str = "Kalibrieren"

    calibrate_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    emergency_off_revealer: Union[Gtk.Revealer, Gtk.Template.Child] = Gtk.Template.Child()
    emergency_off_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new CalibrationPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        try:
            if const.DEBUG:
                self.calibrate_button.set_sensitive(True)
                self.calibrate_button.set_always_show_image(False)
                self.calibrate_button.get_image().stop()

                self.emergency_off_revealer.set_reveal_child(False)

            else:
                if opcua_util.Connection()["main"]["done_referencing"]:
                    self.on_opcua_button_released(None, None, "main", "power_button")

                    return "select_patient"

                else:
                    self.calibrate_button.set_sensitive(False)
                    self.calibrate_button.set_always_show_image(True)
                    self.calibrate_button.get_image().start()

                    self.emergency_off_revealer.set_reveal_child(True)

                    self.if_done_reset()

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)
            self.calibrate_button.set_sensitive(False)
            self.calibrate_button.set_always_show_image(False)
            self.calibrate_button.get_image().stop()

            self.emergency_off_revealer.set_reveal_child(False)

    def prepare_return(self) -> None:
        """Prepare the page to be shown."""
        self.prepare()

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.calibrate_button.connect("clicked", self.on_calibrate_clicked)
        self.emergency_off_button.connect("clicked", self.on_emergency_off_clicked)

    def if_done_reset(self):
        try:
            if not opcua_util.Connection()["main"]["done_referencing"]:
                GLib.timeout_add(1000 / 10, self.if_done_reset)

            else:
                print(
                    "Done calibrating, resetting",
                    opcua_util.Connection()["main"]["done_referencing"],
                )

                opcua_util.Connection()["main"]["reset_axes_button"] = True

                self.if_done_switch_to_next()

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            print("Could not calibrate")

            if const.DEBUG:
                print("(DEBUG) DONE")

                self.if_done_switch_to_next()

    def if_done_switch_to_next(self):
        try:
            if opcua_util.Connection()["main"]["reset_axes_button"]:
                GLib.timeout_add(1000 / 10, self.if_done_switch_to_next)

            else:
                print(
                    "Done resetting, switching to next page",
                    not opcua_util.Connection()["main"]["reset_axes_button"],
                )
                self.on_opcua_button_released(None, None, "main", "power_button")
                self.get_toplevel().switch_page("select_patient")
                self.get_toplevel().clear_history()

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            print("Could not reset")

            if const.DEBUG:
                print("(DEBUG) DONE")
                self.get_toplevel().switch_page("select_patient")
                self.get_toplevel().clear_history()

    def on_calibrate_clicked(self, button: Gtk.Button) -> None:
        """React to the calibrate button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        button.set_sensitive(False)

        opcua_action_queue: List[Tuple[Callable, Tuple[Any, ...]]] = [
            (self.on_opcua_button_released, (button, None, "main", "emergency_off_button"),),
            (self.on_opcua_button_pressed, (button, None, "main", "reset_button")),
            (self.on_opcua_button_released, (button, None, "main", "reset_button")),
            (self.on_opcua_button_pressed, (button, None, "main", "power_button")),
            (self.if_done_reset, ()),
        ]

        def work_action_queue():
            """Work through the action queue with an interval of 400ms."""
            if opcua_action_queue:
                fn, args = opcua_action_queue.pop(0)
                print(fn, args)
                fn(*args)

                GLib.timeout_add(500, work_action_queue)

        work_action_queue()

        button.set_always_show_image(True)
        button.get_image().start()

        self.emergency_off_revealer.set_reveal_child(True)

    def on_emergency_off_clicked(self, button: Gtk.Button) -> None:
        """React to the emergency off button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        self.calibrate_button.set_sensitive(False)
        self.calibrate_button.set_always_show_image(False)
        self.calibrate_button.get_image().stop()

        self.on_opcua_button_pressed(button, None, "main", "emergency_off_button")

        self.prepare()


# Make CalibrationPage accessible via .ui files
GObject.type_ensure(CalibrationPage)
