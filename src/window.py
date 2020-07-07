from gi.repository import Gtk

from . import login_page, select_patient_page, edit_patient_page


@Gtk.Template(resource_path='/de/linusmathieu/Liegensteuerung/window.ui')
class LiegensteuerungWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LiegensteuerungWindow'

    page_stack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.page_stack.set_visible_child_name("page1")
