"""A page that offers the user to edit patient data."""

from typing import Union

from gi.repository import GObject, Gtk  # type: ignore


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/edit_patient_page.ui"
)
class EditPatientPage(Gtk.Box):
    __gtype_name__ = "EditPatientPage"

    button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new EditPatientPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def do_parent_set(self, old_parent: Gtk.Widget):
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Gtk.Widget or None): The old parent
        """
        if self.get_parent() is not None:
            self.button.connect("clicked", print)


GObject.type_ensure(EditPatientPage)
