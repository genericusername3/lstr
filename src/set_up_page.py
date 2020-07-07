from gi.repository import GObject, Gtk
import time


@Gtk.Template(resource_path='/de/linusmathieu/Liegensteuerung/edit_patient_page.ui')
class EditPatientPage(Gtk.Box):
    __gtype_name__ = 'EditPatientPage'

    button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do_parent_set(self, old_parent):
        if self.get_parent() is not None:
            self.button.connect("clicked", print)


GObject.type_ensure(EditPatientPage)
