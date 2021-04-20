"""A page that allows the user to perform a treatment program on a patient."""

from typing import Union, Optional

from gi.repository import GObject, GLib, Gio, Gtk, Rsvg  # type: ignore
import cairo

from .page import Page, PageClass

from .program_util import Program
from .opcua_util import Connection

from . import const


SVG_CODE: str = (
    Gio.resources_lookup_data(
        "/de/linusmathieu/Liegensteuerung/treatment_preview.svg", 0
    )
    .get_data()
    .decode()
)

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
    """

    __gtype_name__ = "TreatmentPage"

    header_visible: bool = True
    title: str = "Behandlung"

    start_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    resume_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    pause_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    cancel_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    cancel_revealer: Union[Gtk.Revealer, Gtk.Template.Child] = Gtk.Template.Child()

    emergency_off_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    visualisation_drawing_area: Union[
        Gtk.DrawingArea, Gtk.Template.Child
    ] = Gtk.Template.Child()
    program_progress_bar: Union[
        Gtk.ProgressBar, Gtk.Template.Child
    ] = Gtk.Template.Child()

    left_right_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    up_down_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    tilt_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    left_pusher_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    right_pusher_label: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    visualising: bool = False

    emergency_off: bool = False

    last_progress: float = 0

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

            Connection()["main"]["setup_mode"] = False

            self.visualising = True

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            self.visualising = const.DEBUG

        if self.visualising:
            self.progress_moving_to = True

            self.visualisation_loop()

        self.start_button.show()
        self.resume_button.hide()
        self.pause_button.hide()
        self.cancel_revealer.set_reveal_child(False)

        if const.DEBUG:
            self.started = False

        self.last_progress = 0

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        try:
            Connection()["main"]["setup_mode"] = False

            self.visualising = True
        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            self.visualising = const.DEBUG

        if self.visualising:
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

        self.emergency_off_button.connect("clicked", self.on_emergency_off_clicked)

        self.visualisation_drawing_area.connect("draw", self.on_draw_visualisation)

    def on_start_clicked(self, button: Gtk.Button) -> None:
        """React to the "Start" button being clicked.

        Start the treatment.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.start_button.hide()
        self.resume_button.hide()
        self.pause_button.show()
        self.cancel_revealer.set_reveal_child(True)

        self.on_opcua_button_pressed(button, None, "main", "start_button")

        if const.DEBUG:
            self.started = True

    def on_pause_clicked(self, button: Gtk.Button) -> None:
        """React to the "Pause" button being clicked.

        Pause the treatment.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.start_button.hide()
        self.resume_button.show()
        self.pause_button.hide()
        self.cancel_revealer.set_reveal_child(True)

        self.on_opcua_button_released(button, None, "main", "start_button")

        if const.DEBUG:
            self.started = False

    def on_resume_clicked(self, button: Gtk.Button) -> None:
        """React to the "Resume" button being clicked.

        Resume the treatment.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.start_button.hide()
        self.resume_button.hide()
        self.pause_button.show()
        self.cancel_revealer.set_reveal_child(True)

        self.on_opcua_button_pressed(button, None, "main", "start_button")

        if const.DEBUG:
            self.started = True

    def on_cancel_clicked(self, button: Gtk.Button) -> None:
        """React to the "Cancel" button being clicked.

        Cancel the treatment.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.start_button.show()
        self.resume_button.hide()
        self.pause_button.hide()
        self.cancel_revealer.set_reveal_child(False)

        self.on_opcua_button_released(button, None, "main", "start_button")
        self.on_opcua_button_released(button, None, "main", "power_button")
        self.on_opcua_button_pressed(button, None, "main", "reset_button")
        GLib.timeout_add(
            500,
            self.on_opcua_button_released,
            button,
            None,
            "main",
            "reset_button",
        )

        self.get_toplevel()._show_page("select_patient", animation_direction=-1)
        self.get_toplevel().clear_history()

        if const.DEBUG:
            self.started = False

    def on_emergency_off_clicked(self, button: Gtk.Button) -> None:
        """React to the "Emergency Off" button being clicked.

        Interrupt the treatment.

        Args:
            button (Gtk.Button): The clicked button
        """
        print("NOTAUS")
        self.emergency_off = not self.emergency_off

        try:
            if self.emergency_off:
                self.on_opcua_button_pressed(
                    button, None, "main", "emergency_off_button"
                )

                self.start_button.set_sensitive(False)
                self.resume_button.set_sensitive(False)
                self.pause_button.set_sensitive(False)
                self.cancel_button.set_sensitive(False)
                self.emergency_off_button.set_sensitive(False)

                def offer_reset():
                    self.emergency_off_button.set_sensitive(True)
                    self.emergency_off_button.set_label("Reset")
                    self.emergency_off_button.set_always_show_image(False)

                    self.emergency_off_button.get_style_context().remove_class(
                        "destructive-action",
                    )
                    self.emergency_off_button.get_style_context().add_class(
                        "suggested-action",
                    )

                GLib.timeout_add(
                    500,
                    offer_reset,
                )

                if const.DEBUG:
                    self.started = False

            else:
                self.start_button.set_sensitive(True)
                self.resume_button.set_sensitive(True)
                self.pause_button.set_sensitive(True)
                self.cancel_button.set_sensitive(True)

                self.get_toplevel()._show_page("calibration", animation_direction=-1)
                self.get_toplevel().clear_history()

                self.emergency_off_button.set_sensitive(True)
                self.emergency_off_button.set_label("NOT AUS")
                self.emergency_off_button.set_always_show_image(True)

                self.emergency_off_button.get_style_context().remove_class(
                    "suggested-action",
                )
                self.emergency_off_button.get_style_context().add_class(
                    "destructive-action",
                )

        except ConnectionRefusedError:
            print("NOTAUS failed")
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

    def if_done_switch_to_next(self):
        try:
            if Connection()["main"]["reset_axes_button"]:
                GLib.timeout_add(1000 / 10, self.if_done_switch_to_next)

            else:
                self.visualising = False

                self.on_opcua_button_released(None, None, "main", "setup_mode")
                self.on_opcua_button_released(None, None, "main", "reset_axes_button")
                self.on_opcua_button_released(None, None, "main", "power_button")

                Connection()["axis0"]["start"] = False
                Connection()["axis1"]["start"] = False
                Connection()["axis2"]["start"] = False
                Connection()["axis3"]["start"] = False
                Connection()["axis4"]["start"] = False

                self.get_toplevel().switch_page("select_patient")
                self.get_toplevel().clear_history()

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            print("Could not reset")

            if const.DEBUG:
                self.get_toplevel().switch_page("select_patient")
                self.get_toplevel().clear_history()

    def visualisation_loop(self) -> None:
        """Repeatedly render an SVG visualisation for the motor values."""
        # FIXME: This whole progress mess doesn't really work

        try:
            prog = self.get_toplevel().active_program
            progress = Connection()["counters"]["passes_total"] / (
                (
                    (prog.push_count_up + 1) * prog.pass_count_up
                    + (prog.push_count_down + 1) * prog.pass_count_down
                )
                * prog.repeat_count
            )

            self.program_progress_bar.set_fraction(progress)

            if self.last_progress > progress:

                def reset():
                    self.on_opcua_button_pressed(None, None, "main", "setup_mode")

                    def start_reset():
                        self.on_opcua_button_pressed(
                            None, None, "main", "reset_axes_button"
                        )
                        self.if_done_switch_to_next()

                    GLib.timeout_add(500, start_reset)

                GLib.timeout_add(500, reset)

            else:
                self.last_progress = progress

        except ConnectionRefusedError:
            self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)

            if not const.DEBUG:
                return

        self.visualisation_drawing_area.queue_draw()

        if self.visualising:
            GLib.timeout_add(
                1000 / 30, self.visualisation_loop, priority=GLib.PRIORITY_HIGH
            )
        else:
            print("visualising is False")

    def on_draw_visualisation(self, widget: Gtk.Widget, cr: cairo.Context) -> None:
        """React to the visualisation being queried to be drawn. Draw the visualisation.

        Args:
            widget (Gtk.Widget): The widget to re-draw
            cr (cairo.Context): The cairo.Context to draw on/with
        """
        if not self.visualising:
            return

        try:
            left_right = Connection()["axis2"]["current_position"]
            up_down = Connection()["axis3"]["current_position"]
            tilt = Connection()["axis4"]["current_position"]
            left_pusher = Connection()["axis0"]["current_position"]
            right_pusher = Connection()["axis1"]["current_position"]
            is_pusher_active = Connection()["main"]["is_pusher_active"]

        except ConnectionRefusedError:
            if const.DEBUG:
                import math
                import time

                if self.started or not hasattr(self, "lasttime"):
                    self.lasttime = time.time()

                left_right = int(math.sin(self.lasttime / 2) * 25)
                up_down = int(math.sin(self.lasttime / 2.5) * 50)
                tilt = int(math.sin(self.lasttime / 1.5) * 27)
                left_pusher = int(math.sin(self.lasttime / 1.75) * 25 + 25)
                right_pusher = int(math.sin(self.lasttime / 2.25) * 25 + 25)

                is_pusher_active = self.started

            else:
                self.get_toplevel().show_error(const.CONNECTION_ERROR_TEXT)
                self.visualising = False
                return

        style_ctx: Gtk.StyleContext = widget.get_style_context()

        fg_color = style_ctx.get_color(style_ctx.get_state())

        svg: str = SVG_CODE.format(
            fg_color=f"rgb({fg_color.red}, {fg_color.green}, {fg_color.blue})",
            moving_color="teal"
            if is_pusher_active
            else "#dd4444"
            if self.emergency_off
            else f"rgb({(fg_color.red + 1) / 3}, "
            + f"{(fg_color.green + 1) / 3}, "
            + f"{(fg_color.blue + 1) / 3})",
            up_down=max(-55, min(55, up_down)) * UP_DOWN_FACTOR,
            rotation=-max(-27, min(27, tilt)),
            left_pusher=25 - max(0, min(50, left_pusher)),
            right_pusher=25 - max(0, min(50, right_pusher)),
        )

        self.left_right_label.set_text(str(left_right))
        self.up_down_label.set_text(str(up_down))
        self.tilt_label.set_text(str(tilt))
        self.left_pusher_label.set_text(str(left_pusher))
        self.right_pusher_label.set_text(str(right_pusher))

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
