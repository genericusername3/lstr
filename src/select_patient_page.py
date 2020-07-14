"""A page that prompts the user to select a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from .patient_util import Patient
from .patient_row import PatientRow, PatientHeader


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/select_patient_page.ui"
)
class SelectPatientPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to select a patient.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "SelectPatientPage"

    header_visible: bool = True
    title: str = "Patient auswählen"

    patient_list_box: Union[
        Gtk.ListBox, Gtk.Template.Child
    ] = Gtk.Template.Child()

    header_box: Union[Gtk.Box, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new SelectPatientPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        self.patient_list_box.bind_model(
            Patient.iter_to_model(Patient.get_all()), PatientRow
        )
        self.patient_list_box.show_all()

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.header_box.pack_start(
            PatientHeader(), fill=True, expand=True, padding=0
        )
        self.header_box.show_all()

        self.patient_list_box.connect("row-selected", self.on_patient_selected)

    def on_patient_selected(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow):
        if row is not None:
            self.get_toplevel().active_patient = row.get_child().patient

            self.get_toplevel().switch_page(
                "pain_evaluation", row.get_child().patient
            )
        list_box.unselect_all()


# Make SelectPatientPage accessible via .ui files
GObject.type_ensure(SelectPatientPage)
