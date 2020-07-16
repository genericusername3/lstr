"""Summary
"""
import sys
import gi
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gio, Gdk, Gtk

from .window import LiegensteuerungWindow


class LstrgApplication(Gtk.Application):
    """The Gtk.Application that represents the Liegensteuerung."""

    def __init__(self):
        """Create a new LstrgApplication."""
        super().__init__(
            application_id='de.linusmathieu.Liegensteuerung',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        css_provider: Gtk.CssProvider = Gtk.CssProvider()
        css_provider.load_from_resource(
            "/de/linusmathieu/Liegensteuerung/liegensteuerung.css"
        )

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        if "HighContrast" in Gtk.Settings.get_default().props.gtk_theme_name:
            css_provider_contrast: Gtk.CssProvider = Gtk.CssProvider()
            css_provider_contrast.load_from_resource(
                "/de/linusmathieu/Liegensteuerung/highcontrast.css"
            )
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider_contrast,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
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
