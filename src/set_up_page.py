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

    camera_frame: numpy.ndarray = None
    running: bool = True
    cam_available: bool = True

    end_value_left: int = 0
    end_value_right: int = 0

    def __init__(self, **kwargs):
        """Create a new SetupPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

        read_thread = Thread(target=self.read_camera_input_loop)
        read_thread.start()

        self.display_camera_input_loop()

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        pass

    def read_camera_input_loop(self) -> None:
        """Try to store an image from the webcam in camera_frame.

        This only happens if running is True and a webcam could be found.
        """
        video_capture = cv2.VideoCapture(0)

        if video_capture.isOpened():  # try to get the first frame
            while self.running:
                return_value, new_camera_frame = video_capture.read()

                # Some operations like de-noising or color correction could go here

                self.camera_frame = new_camera_frame
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

        self.camera_drawing_area.connect(
            "draw", self.on_draw_camera_drawing_area
        )

        self.ok_button.connect(
            "clicked", self.on_ok_clicked
        )

    def display_camera_input_loop(self) -> None:
        """Read from camera_frame to display the most recent webcam image."""
        if self.camera_frame is not None:
            self.camera_drawing_area.queue_draw()

        if self.running:
            GLib.timeout_add(1000 / 60, self.display_camera_input_loop)

    def do_destroy(self) -> None:
        """When the window is destroyed, stop all threads and quit."""
        self.running = False

    def on_draw_camera_drawing_area(
        self, widget: Gtk.Widget, cr: cairo.Context
    ) -> None:
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
        self.get_toplevel().switch_page("select_program")



GObject.type_ensure(SetupPage)


# avg([float(s) for s in x.split("\n")])
