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
        try:
            # FIXME uncomment all this and remove the "if True:"

            # if not opcua_util.Connection()["main"]["not_referenced"]:
            #     self.on_opcua_button_released(None, None, "main", "power_button")

            #     return "select_patient"

            # elif not opcua_util.Connection()["main"]["referencing"]:

            if True:
                self.calibrate_button.set_sensitive(True)
                self.calibrate_button.set_always_show_image(False)
                self.calibrate_button.get_image().stop()

                self.emergency_off_revealer.set_reveal_child(False)

            # else:
            #     self.calibrate_button.set_sensitive(False)
            #     self.calibrate_button.set_always_show_image(True)
            #     self.calibrate_button.get_image().start()

            #     self.emergency_off_revealer.set_reveal_child(True)

            #     self.if_done_switch_to_next()

        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")
            self.calibrate_button.set_sensitive(False)
            self.calibrate_button.set_always_show_image(False)
            self.calibrate_button.get_image().stop()

            self.emergency_off_revealer.set_reveal_child(False)

            # FIXME Remove this --- debug purposes only
            GLib.timeout_add(
                3000,
                lambda: (
                    self.get_toplevel().switch_page("select_patient"),
                    self.get_toplevel().clear_history(),
                ),
            )

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
        self.emergency_off_button.connect(
            "clicked", self.on_emergency_off_button_clicked
        )

    def if_done_switch_to_next(self):
        if opcua_util.Connection()["main"]["referencing"]:
            GLib.timeout_add(1000 / 10, self.if_done_switch_to_next)

        else:
            print("DONE", opcua_util.Connection()["main"]["referencing"])
            self.on_opcua_button_released(None, None, "main", "power_button")
            self.get_toplevel().switch_page("select_patient")
            self.get_toplevel().clear_history()

    def on_calibrate_clicked(self, button: Gtk.Button) -> None:
        """React to the calibrate button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        button.set_sensitive(False)

        self.on_opcua_button_pressed(button, None, "main", "power_button")
        opcua_util.Connection()["main"]["referencing"] = True

        button.set_always_show_image(True)
        button.get_image().start()

        self.emergency_off_revealer.set_reveal_child(True)

        self.if_done_switch_to_next()

        # FIXME Remove this --- debug purposes only
        GLib.timeout_add(
            5000,
            lambda: (
                self.get_toplevel().switch_page("select_patient"),
                self.get_toplevel().clear_history(),
            ),
        )

    def on_emergency_off_clicked(self, button: Gtk.Button) -> None:
        """React to the emergency off button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        self.calibrate_button.set_sensitive(False)
        self.calibrate_button.set_always_show_image(False)
        self.calibrate_button.get_image().stop()

        self.emergency_off_button.set_sensitive(False)

        self.on_opcua_button_pressed(button, None, "main", "emergency_off_button")

        def resume():
            self.on_opcua_button_pressed(button, None, "main", "emergency_off_button")
            GLib.timeout_add(500, reset)

        def reset():
            self.on_opcua_button_pressed(button, None, "main", "reset_button")
            self.get_toplevel()._show_page("calibration", animation_direction=0)

        GLib.timeout_add(1000, resume)


# Make CalibrationPage accessible via .ui files
GObject.type_ensure(CalibrationPage)
