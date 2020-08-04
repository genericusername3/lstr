"""A page that offers the user to manually set up the motors."""

from typing import Optional, Union

from gi.repository import GObject  # type: ignore
from gi.repository import GLib  # type: ignore
from gi.repository import GdkPixbuf  # type: ignore
from gi.repository import Gdk  # type: ignore
from gi.repository import Gtk  # type: ignore

import cairo

import cv2  # type: ignore
import numpy  # type: ignore

from threading import Thread  # type: ignore

from .page import Page, PageClass
from .opcua_util import Connection


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/set_up_page.ui")
class SetupPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that offers the user to manually set up the motors.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        cam_available (bool): Whether a camera is connected
        camera_drawing_area (Gtk.DrawingArea or Gtk.Template.Child): The
            Gtk.DrawingArea to display the camera output in.
        camera_frame (numpy.ndarray): The current frame as an numpy.ndarray
        running (bool): Whether a camera output should be shown
    """

    __gtype_name__ = "SetupPage"

    header_visible: bool = True
    title: str = "Einrichten"

    camera_drawing_area: Union[
        Gtk.Template.Child, Gtk.DrawingArea
    ] = Gtk.Template.Child()

    ok_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()

    reset_axes_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    # Tilt buttons
    tilt_down_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    tilt_up_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    # Pusher buttons
    left_move_in_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    left_move_out_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    right_move_in_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    right_move_out_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    # Movement buttons
    move_left_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    move_right_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    move_up_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    move_down_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    save_position_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()

    up_down_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()
    left_right_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()
    tilt_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()
    left_pusher_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()
    right_pusher_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()

    end_pos_left_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()
    end_pos_right_label: Union[Gtk.Label, Gtk.Template.Child] = Gtk.Template.Child()

    camera_frame: numpy.ndarray = None
    running: bool = True
    cam_available: bool = True

    end_value_left: Optional[int] = None
    end_value_right: Optional[int] = None

    def __init__(self, **kwargs):
        """Create a new SetupPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        try:
            Connection()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

        self.running = True

        self.end_value_left = None
        self.end_value_right = None

        read_thread = Thread(target=self.read_camera_input_loop)
        read_thread.start()

        self.ok_button.set_sensitive(False)

        self.display_camera_input_loop()
        self.update_labels_loop()

    def prepare_return(self) -> None:
        """Prepare the page to be shown."""
        try:
            Connection()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

        self.running = True

        read_thread = Thread(target=self.read_camera_input_loop)
        read_thread.start()

        self.display_camera_input_loop()
        self.update_labels_loop()

    def unprepare(self):
        """Prepare the page to be hidden."""
        self.running = False

    def read_camera_input_loop(self) -> None:
        """Try to store an image from the webcam in camera_frame.

        This only happens if running is True and a webcam could be found.
        """
        video_capture = cv2.VideoCapture(0)

        if video_capture.isOpened():  # try to get the first frame
            while self.running:
                return_value, new_camera_frame = video_capture.read()

                try:
                    # Some operations like color correction
                    new_camera_frame = cv2.cvtColor(new_camera_frame, cv2.COLOR_BGR2RGB)

                    self.camera_frame = new_camera_frame
                except cv2.error:
                    pass
        else:
            print("No cam found.")
            self.cam_available = False

        video_capture.release()

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.camera_drawing_area.connect("draw", self.on_draw_camera_drawing_area)

        self.ok_button.connect("clicked", self.on_ok_clicked)

        self.save_position_button.connect("clicked", self.on_save_pos_clicked)

        self.reset_axes_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "reset_axes_button",
        )
        self.reset_axes_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "reset_axes_button",
        )

        # Tilt buttons
        self.tilt_down_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "tilt_down_button",
        )
        self.tilt_down_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "tilt_down_button",
        )
        self.tilt_up_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "tilt_up_button",
        )
        self.tilt_up_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "tilt_up_button",
        )

        # Pusher buttons
        self.left_move_in_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "left_move_in_button",
        )
        self.left_move_in_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "left_move_in_button",
        )
        self.left_move_out_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "left_move_out_button",
        )
        self.left_move_out_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "left_move_out_button",
        )
        self.right_move_in_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "right_move_in_button",
        )
        self.right_move_in_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "right_move_in_button",
        )
        self.right_move_out_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "right_move_out_button",
        )
        self.right_move_out_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "right_move_out_button",
        )

        # Movement buttons
        self.move_left_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "move_left_button",
        )
        self.move_left_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "move_left_button",
        )
        self.move_right_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "move_right_button",
        )
        self.move_right_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "move_right_button",
        )
        self.move_up_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "move_up_button",
        )
        self.move_up_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "move_up_button",
        )
        self.move_down_button.connect(
            "button-press-event",
            self.on_opcua_button_pressed,
            "setup",
            "move_down_button",
        )
        self.move_down_button.connect(
            "button-release-event",
            self.on_opcua_button_released,
            "setup",
            "move_down_button",
        )

    def display_camera_input_loop(self) -> None:
        """Read from camera_frame to display the most recent webcam image."""
        if self.camera_frame is not None:
            self.camera_drawing_area.queue_draw()

        if self.running:
            GLib.timeout_add(1000 / 60, self.display_camera_input_loop)

    def update_labels_loop(self) -> None:
        """Read OPC UA values to display current motor status."""
        try:
            Connection()
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")
            return

        self.up_down_label.set_text(str(Connection()["setup"]["up_down"]))
        self.left_right_label.set_text(str(Connection()["setup"]["left_right"]))
        self.tilt_label.set_text(str(Connection()["setup"]["tilt"]))
        self.left_pusher_label.set_text(str(Connection()["setup"]["left_pusher"]))
        self.right_pusher_label.set_text(str(Connection()["setup"]["right_pusher"]))

        self.end_pos_left_label.set_text(
            str(self.end_value_left) if self.end_value_left is not None else "-"
        )
        self.end_pos_right_label.set_text(
            str(self.end_value_right) if self.end_value_right is not None else "-"
        )

        if self.running:
            GLib.timeout_add(1000 / 10, self.update_labels_loop)

    def do_destroy(self) -> None:
        """When the window is destroyed, stop all threads and quit."""
        self.running = False

    def on_draw_camera_drawing_area(
        self, widget: Gtk.Widget, cr: cairo.Context
    ) -> None:
        """React to the camera output being queried to be drawn. Draw the camera output.

        Args:
            widget (Gtk.Widget): The widget to re-draw
            cr (cairo.Context): The cairo.Context to draw on/with
        """
        if self.camera_frame is not None:
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                self.camera_frame.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                len(self.camera_frame[0]),
                len(self.camera_frame),
                3 * len(self.camera_frame[0]),
            )

            available_width = self.camera_drawing_area.get_allocated_width()
            available_height = self.camera_drawing_area.get_allocated_height()

            width = float(pixbuf.get_width())
            height = float(pixbuf.get_height())

            scale = min(available_width / width, available_height / height)

            if scale < 1:
                pixbuf = pixbuf.scale_simple(
                    width * scale, height * scale, GdkPixbuf.InterpType.TILES
                )
            else:
                pixbuf = pixbuf.scale_simple(
                    width * scale, height * scale, GdkPixbuf.InterpType.NEAREST
                )

            Gdk.cairo_set_source_pixbuf(
                cr,
                pixbuf,
                available_width / 2 - width * scale / 2,
                available_height / 2 - height * scale / 2,
            )
            cr.paint()

    def on_ok_clicked(self, button: Gtk.Button) -> None:
        """React to the "OK" button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        self.get_toplevel().switch_page(
            "select_program", self.end_value_left, self.end_value_right
        )  # TODO: Use actual values

    def on_save_pos_clicked(self, button: Gtk.Button) -> None:
        """React to the "Save position" button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        try:
            self.end_value_left = Connection()["setup"]["left_pusher"]
            self.end_value_right = Connection()["setup"]["right_pusher"]
        except ConnectionRefusedError:
            self.get_toplevel().show_error("Die Liege wurde nicht erkannt")

            self.end_value_left = 99999999999
            self.end_value_right = 99999999999

            self.end_pos_left_label.set_text(str(self.end_value_left))
            self.end_pos_right_label.set_text(str(self.end_value_right))

        if self.end_value_left is not None and self.end_value_right is not None:
            self.ok_button.set_sensitive(True)


GObject.type_ensure(SetupPage)


# avg([float(s) for s in x.split("\n")])
