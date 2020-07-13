"""Summary
"""
import sys
import gi
import subprocess

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .window import LiegensteuerungWindow


class LstrgApplication(Gtk.Application):
    """The Gtk.Application that represents the Liegensteuerung."""

    def __init__(self):
        """Create a new LstrgApplication."""
        super().__init__(
            application_id='de.linusmathieu.Liegensteuerung',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        """React to the Application activation ie. opeing a new window."""
        win = self.props.active_window
        if not win:
            win = LiegensteuerungWindow(application=self)
        win.present()


def main(version):
    """Run Liegensteuerung.

    Args:
        version (str): The app version

    Returns:
        int: A return code
    """
    app = LstrgApplication()
    return app.run(sys.argv)
