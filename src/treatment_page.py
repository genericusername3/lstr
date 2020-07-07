from gi.repository import GObject, Gtk


@Gtk.Template(resource_path='/de/linusmathieu/Liegensteuerung/select_patient_page.ui')
class SelectPatientPage(Gtk.Box):
    __gtype_name__ = 'SelectPatientPage'

    label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


GObject.type_ensure(SelectPatientPage)
