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
    visualisation_image: Union[Gtk.Image, Gtk.Template.Child] = Gtk.Template.Child()

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

        self.visualisation_scroller.connect(
            "size-allocate", self.on_visualisation_size_allocated
        )

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

    def on_visualisation_size_allocated(
        self, widget: Gtk.Widget, allocation: Gdk.Rectangle
    ):
        """React to the size of the visualisation scroller being set. Render visualisation.

        Args:
            widget (Gtk.Widget): The visualisation widget
            allocation (Gdk.Rectangle): The new allocation
        """
        if not self.visualising:
            self.visualising = True
            self.visualisation_loop()

    def visualisation_loop(self) -> None:
        """Repeatedly render an SVG visualisation for the motor values."""
        self.render_svg()

        if self.visualising:
            GLib.timeout_add(1000 / 60, self.visualisation_loop)

    def render_svg(self, allocation: Optional[Gdk.Rectangle] = None) -> None:
        """Insert the current values of the motors into the SVG code and display the SVG.

        Args:
            allocation (Gdk.Rectangle, optional): A Gdk.Rectangle that is the size of
                the available space, or None (default) to automatically detect
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

        print(svg)

        handle = Rsvg.Handle.new_from_data(svg.encode())

        dimensions = handle.get_dimensions()

        width: float = float(dimensions.width)
        height: float = float(dimensions.height)

        available_width: int
        available_height: int

        if allocation is None:
            available_width = self.visualisation_scroller.get_allocated_width()
            available_height = self.visualisation_scroller.get_allocated_height()
        else:
            available_width, available_height = (
                allocation.width,
                allocation.height,
            )

        scale: float = min(available_width / width, available_height / height)

        width = dimensions.width * scale
        height = dimensions.height * scale

        svg_surface = cairo.SVGSurface("treatment_preview.svg", width, height)
        ctx = cairo.Context(svg_surface)

        ctx.scale(scale, scale)

        handle.render_cairo(ctx)

        pixbuf = Gdk.pixbuf_get_from_surface(
            svg_surface, src_x=0, src_y=0, width=width, height=height,
        )

        self.visualisation_image.set_from_pixbuf(pixbuf)


# Make TreatmentPage accessible via .ui files
GObject.type_ensure(TreatmentPage)
