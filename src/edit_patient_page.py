"""A page that prompts the user to select a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from . import patient_util


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/edit_patient_page.ui"
)
class EditPatientPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to view, edit or create a patient.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "EditPatientPage"

    header_visible: bool = True
    title: str = "Patient hinzufügen"

    patient: Optional[patient_util.Patient] = None

    # %%WIDGET_NAME%%: Union[Gtk.Widget, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new EditPatientPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, patient: Optional[patient_util.Patient] = None) -> None:
        """Prepare the page to be shown."""
        self.patient = patient

        if patient is not None:
            self.title = f"{patient.first_name} {patient.last_name}"

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        # Connect events


# Make EditPatientPage accessible via .ui files
GObject.type_ensure(EditPatientPage)
