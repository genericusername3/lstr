"""A page that prompts the user to select a patient."""

from typing import Union, Optional, Any, Tuple

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from .patient_util import Patient
from .patient_util import COLUMNS as PATIENT_COLUMNS
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

    add_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    patient_search_entry: Union[
        Gtk.SearchEntry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    sort_column: int = PATIENT_COLUMNS.index("last_name")
    sort_reverse: bool = False

    def __init__(self, **kwargs):
        """Create a new SelectPatientPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        print("prepare sel_pat")

        self.get_toplevel().active_patient = None

        self.sort_column = PATIENT_COLUMNS.index("last_name")
        self.sort_reverse = False

        self.header_box.get_children()[1].update_sort_icons()

        self.patient_search_entry.set_text("")
        self.update_patients()

        self.patient_search_entry.grab_focus()

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        print("prepare_return sel_pat")

        self.get_toplevel().active_patient = None

        # Inefficient to re-load all patients, but everything else is more work
        self.update_patients()

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
            PatientHeader(self), fill=True, expand=True, padding=0
        )
        self.header_box.show_all()

        self.patient_list_box.connect("row-selected", self.on_patient_selected)

        self.add_button.connect("clicked", self.on_add_clicked)

        self.patient_search_entry.connect(
            "search-changed", self.on_search_changed
        )
        self.patient_search_entry.connect(
            "focus-in-event", self.on_focus_entry
        )
        self.patient_search_entry.connect(
            "button-press-event", self.on_entry_button_press
        )
        self.patient_search_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.patient_search_entry.connect(
            "focus-out-event", self.on_unfocus_entry
        )

    def on_patient_selected(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow):
        """React to the user selecting a patient.

        This will switch to the page 'pain_evaluation'.

        Args:
            list_box (Gtk.ListBox): The Gtk.ListBox that is the row's parent
            row (Gtk.ListBoxRow): The Gtk.ListBoxRow that was selected
        """
        if row is not None:
            self.get_toplevel().active_patient = row.get_child().patient

            self.get_toplevel().switch_page("pain_evaluation")
        list_box.unselect_all()

    def on_add_clicked(self, button: Gtk.Button) -> None:
        """React to the "add patient" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page("edit_patient")

    def update_patients(self) -> None:
        """Re-query and re-sort all patients."""
        if self.patient_search_entry.get_text() == "":
            self.patient_list_box.bind_model(
                Patient.iter_to_model(
                    Patient.get_all(
                        sort_key_func=self.sort_key, reverse=self.sort_reverse
                    )
                ),
                PatientRow,
            )
        else:
            self.patient_list_box.bind_model(
                Patient.iter_to_model(
                    Patient.get_for_query(
                        self.patient_search_entry.get_text(),
                        sort_key_func=self.sort_key,
                        reverse=self.sort_reverse,
                    )
                ),
                PatientRow,
            )

        self.patient_list_box.show_all()

    def on_search_changed(self, search_entry: Gtk.SearchEntry) -> None:
        """React to the search query being changed by the user.

        Args:
            search_entry (Gtk.SearchEntry): The search entry that the user
                entered the query into
        """
        self.update_patients()

    def sort_key(self, patient_row: Tuple[Any, ...]) -> Any:
        """Return a sort key for a patient row.

        Args:
            patient_row (Tuple[Any, ...]): The patient row

        Returns:
            Any: An object by which patient_row can be sorted
        """
        return patient_row[self.sort_column]

    def set_sort(self, column_index: int, reverse: bool) -> None:
        """Set the sort parameters and sort the patients if necessary.

        Args:
            column_index (int): The index of the column by which to sort
            reverse (bool): Whether to reverse the sorted rows
        """
        if reverse != self.sort_reverse or column_index != self.sort_column:
            self.sort_column = column_index
            self.sort_reverse = reverse
            self.update_patients()


# Make SelectPatientPage accessible via .ui files
GObject.type_ensure(SelectPatientPage)
