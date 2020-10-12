"""A page that allows the user to perform a treatment program on a patient."""

from typing import Union, Optional

from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Rsvg  # type: ignore
import cairo

from .page import Page, PageClass

from .program_util import Program
from .opcua_util import Connection


SVG_CODE: str = Gio.resources_lookup_data(
    "/de/linusmathieu/Liegensteuerung/treatment_preview.svg", 0
).get_data().decode()

LEFT_RIGHT_FACTOR: float = 50.0 / 18.0
LEFT_RIGHT_SCALE_FACTOR: float = LEFT_RIGHT_FACTOR / (1000.0 / 3.0)
UP_DOWN_FACTOR: float = 0.5


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/treatment_page.ui")
class TreatmentPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that allows the user to perform a treatment program on a patient.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "TreatmentPage"

    header_visible: bool = True
    title: str = "Behandlung"

    start_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    resume_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    pause_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    cancel_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    emergency_off_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    visualisation_drawing_area: Union[
        Gtk.DrawingArea, Gtk.Template.Child
    ] = Gtk.Template.Child()

    left_right_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    up_down_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    tilt_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    left_pusher_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    right_pusher_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    visualising: bool = False

    def __init__(self, **kwargs):
        """Create a new TreatmentPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        program: Program = self.get_toplevel().active_program

        try:
            for key in Connection()["program"].keys():
                Connection()["program"][key] = program[key]

            self.visualising = True
            self.visualisation_loop()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

            self.visualising = False

        self.start_button.show()
        self.resume_button.hide()
        self.pause_button.hide()
        self.cancel_button.hide()

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        try:
            Connection()

            self.visualising = True
            self.visualisation_loop()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

            self.visualising = False

    def unprepare(self) -> None:
        """Prepare the page to be hidden."""
        self.visualising = False

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.start_button.connect("clicked", self.on_start_clicked)
        self.pause_button.connect("clicked", self.on_pause_clicked)
        self.resume_button.connect("clicked", self.on_resume_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)

        self.emergency_off_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "main",
            "emergency_off_button",
        )
        self.emergency_off_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "main",
            "emergency_off_button",
        )

        self.visualisation_drawing_area.connect("draw", self.on_draw_visualisation)

    def on_start_clicked(self, button: Gtk.Button) -> None:
        """React to the "Start" button being clicked.

        Start the treatment.

        Args:
            button (Gtk.Button): Teh clicked button
        """
        self.start_button.hide()
        self.resume_button.hide()
        self.pause_button.show()
        self.cancel_button.show()

        self.on_opcua_button_pressed(button, None, "main", "start_button")

    def on_pause_clicked(self, button: Gtk.Button) -> None:
        """React to the "Pause" button being clicked.

        Start the treatment.

        Args:
            button (Gtk.Button): Teh clicked button
        """
        self.start_button.hide()
        self.resume_button.show()
        self.pause_button.hide()
        self.cancel_button.show()

        self.on_opcua_button_released(button, None, "main", "start_button")

    def on_resume_clicked(self, button: Gtk.Button) -> None:
        """React to the "Resume" button being clicked.

        Start the treatment.

        Args:
            button (Gtk.Button): Teh clicked button
        """
        self.start_button.hide()
        self.resume_button.hide()
        self.pause_button.show()
        self.cancel_button.show()

        self.on_opcua_button_pressed(button, None, "main", "start_button")

    def on_cancel_clicked(self, button: Gtk.Button) -> None:
        """React to the "Cancel" button being clicked.

        Start the treatment.

        Args:
            button (Gtk.Button): Teh clicked button
        """
        self.start_button.show()
        self.resume_button.hide()
        self.pause_button.hide()
        self.cancel_button.hide()

        self.on_opcua_button_released(button, None, "main", "start_button")
        self.on_opcua_button_released(button, None, "main", "power_button")
        self.on_opcua_button_pressed(button, None, "main", "reset_button")

        self.get_toplevel().switch_page("select_patient")

    def visualisation_loop(self) -> None:
        """Repeatedly render an SVG visualisation for the motor values."""
        try:
            Connection()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")
            return

        self.visualisation_drawing_area.queue_draw()

        if self.visualising:
            GLib.timeout_add(1000 / 60, self.visualisation_loop)

    def on_draw_visualisation(self, widget: Gtk.Widget, cr: cairo.Context) -> None:
        """React to the visualisation being queried to be drawn. Draw the visualisation.

        Args:
            widget (Gtk.Widget): The widget to re-draw
            cr (cairo.Context): The cairo.Context to draw on/with
        """
        try:
            Connection()
        except ConnectionRefusedError:
            # self.get_toplevel().show_error("Die Liege wurde nicht erkannt")
            self.visualising = False
            return

        style_ctx: Gtk.StyleContext = widget.get_style_context()

        svg: str = SVG_CODE.format(
            fg_color=style_ctx.get_color(style_ctx.get_state()).to_string(),
            moving_color="teal"
            if Connection()["main"]["is_pusher_active"]
            else "#d8d8d8",
            up_down=Connection()["main"]["up_down"] * UP_DOWN_FACTOR,
            rotation=Connection()["main"]["tilt"],
            left_pusher=25 - Connection()["main"]["left_pusher"],
            right_pusher=25 - Connection()["main"]["right_pusher"],
        )

        self.left_right_label.set_text(str(Connection()["main"]["left_right"]))
        self.up_down_label.set_text(str(Connection()["main"]["up_down"]))
        self.tilt_label.set_text(str(Connection()["main"]["tilt"]))
        self.left_pusher_label.set_text(str(Connection()["main"]["left_pusher"]))
        self.right_pusher_label.set_text(str(Connection()["main"]["right_pusher"]))

        handle = Rsvg.Handle.new_from_data(svg.encode())

        available_width = self.visualisation_drawing_area.get_allocated_width()
        available_height = self.visualisation_drawing_area.get_allocated_height()

        dimensions = handle.get_dimensions()

        width = float(dimensions.width)
        height = float(dimensions.height)

        scale = min(available_width / width, available_height / height)

        cr.translate(
            (available_width - width * scale) / 2.0,
            (available_height - height * scale) / 2.0,
        )
        cr.scale(scale, scale)

        handle.render_cairo(cr)


# Make TreatmentPage accessible via .ui files
GObject.type_ensure(TreatmentPage)
