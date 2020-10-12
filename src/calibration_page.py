"""A page that prompts the user to input the patient's pain values."""

from typing import Union, Optional

from gi.repository import GObject, GLib, Gtk  # type: ignore

from .page import Page, PageClass

from . import opcua_util


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

    emergency_off_revealer: Union[
        Gtk.Revealer, Gtk.Template.Child
    ] = Gtk.Template.Child()
    emergency_off_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new CalibrationPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        self.calibrate_button.set_sensitive(True)
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

    def on_calibrate_clicked(self, button: Gtk.Button) -> None:
        """React to the calibrate button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        button.set_sensitive(False)

        # TODO: Wait until the calibration is done

        def if_done_switch_to_next():
            if opcua_util.Connection()["main"]["reset"]:
                GLib.timeout_add(1000 / 10, if_done_switch_to_next)
            else:
                self.get_toplevel().switch_page("select_patient")
                self.get_toplevel().clear_history()

        self.on_opcua_button_pressed(button, None, "main", "reset")

        try:
            if opcua_util.Connection()["main"]["reset"]:
                button.set_always_show_image(True)
                button.get_image().start()

                self.emergency_off_revealer.set_reveal_child(True)

                if_done_switch_to_next()

        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")


# Make CalibrationPage accessible via .ui files
GObject.type_ensure(CalibrationPage)
