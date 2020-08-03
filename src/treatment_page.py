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

    visualisation_scroller: Union[
        Gtk.ScrolledWindow, Gtk.Template.Child
    ] = Gtk.Template.Child()
    visualisation_drawing_area: Union[
        Gtk.DrawingArea, Gtk.Template.Child
    ] = Gtk.Template.Child()

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
        # for key in Connection()["program"].keys():
        #     Connection()["program"][key] = program[key]

        self.start_button.show()
        self.resume_button.hide()
        self.pause_button.hide()
        self.cancel_button.hide()

        self.visualising = True
        self.visualisation_loop()

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        self.visualising = True
        self.visualisation_loop()

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
            "clicked", self.on_opcua_button_clicked, "main", "emergency_off_button",
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

    def visualisation_loop(self) -> None:
        """Repeatedly render an SVG visualisation for the motor values."""
        self.visualisation_drawing_area.queue_draw()

        if self.visualising:
            GLib.timeout_add(1000 / 60, self.visualisation_loop)

    def on_draw_visualisation(self, widget: Gtk.Widget, cr: cairo.Context) -> None:
        """React to the visualisation being queried to be drawn. Draw the visualisation.

        Args:
            widget (Gtk.Widget): Description
            cr (cairo.Context): Description
        """
        import time, math

        svg: str = SVG_CODE.format(
            fg_color="#888",
            pusher_color="#669",
            left_right=math.sin(time.time() * 0.71) * 50,
            left_right_scale=(
                0.7 + ((50 - (math.sin(time.time() * 0.71) * 50)) / 333.3333)
            ),
            up_down=math.sin(time.time() * 0.77) * 50,
            rotation=math.sin(time.time() * 0.93) * 50,
            left_pusher=math.sin(time.time() * 0.97) * 25,
            right_pusher=math.sin(time.time() * 0.53) * 25,
        )

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
