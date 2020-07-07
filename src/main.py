import sys
import gi
import subprocess

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .window import LiegensteuerungWindow


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='de.linusmathieu.Liegensteuerung',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )


    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = LiegensteuerungWindow(application=self)
        win.present()


def main(version):
    app = Application()
    return app.run(sys.argv)
