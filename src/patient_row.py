"""A widget that represents one patient in horizontal orientation.

Ideal for viewing patients in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, Optional, List

from datetime import datetime
from fuzzywuzzy import fuzz

from gi.repository import GLib, Gtk  # type: ignore

from . import patient_util


size_groups: Dict[str, Gtk.SizeGroup] = {}

COLUMN_HEADER_TRANSLATIONS: Dict[str, str] = {
    "patient_id": "Nr.",
    "first_name": "Vorname",
    "last_name": "Nachname",
    "gender": "Geschlecht",
    "birthday": "Geburtsdatum",
}


class PatientRow(Gtk.Box):
    """A widget that represents one patient in horizontal orientation.

    Ideal for viewing patients in lists, because all columns are added to a
        Gtk.SizeGroup

    This widget contains a button that offers the user to view more information
        about the patient and edit patient data.
    """

    patient: patient_util.Patient

    def __init__(self, patient: patient_util.Patient):
        """Create a new PatientRow.

        Args:
            patient (patient_util.Patient): The patient to represent

        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.pack_start(h_box, expand=True, fill=True, padding=0)

        self.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            expand=True,
            fill=True,
            padding=0,
        )

        self.patient = patient

        for column in patient_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = GLib.markup_escape_text(str(patient.__dict__.get(column)))

            if column in patient_util.DATE_COLUMNS:
                text = (
                    "<tt>"
                    + datetime.fromisoformat(text).strftime("%d.%m.%Y")
                    + "</tt>"
                )

            cell_label = Gtk.Label(label=text, use_markup=True)

            cell_label.set_size_request(-1, 32)
            cell_label.set_halign(Gtk.Align.START)
            cell_label.set_margin_start(4)
            cell_label.set_xalign(0)

            size_groups[column].add_widget(cell_label)

            h_box.pack_start(cell_label, expand=True, fill=True, padding=4)

            h_box.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                expand=False,
                fill=False,
                padding=4,
            )

        if size_groups.get("INFO_BUTTON", None) is None:
            size_groups["INFO_BUTTON"] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

        info_button: Gtk.Button = Gtk.Button.new_from_icon_name(
            "dialog-information-symbolic", Gtk.IconSize.BUTTON
        )
        info_button.set_size_request(48, 48)
        info_button.set_border_width(2)
        info_button.connect("clicked", self.on_info_clicked)

        size_groups["INFO_BUTTON"].add_widget(info_button)

        h_box.pack_start(info_button, expand=False, fill=False, padding=4)

        self.show_all()

    @staticmethod
    def matches_query(list_box_row: Gtk.ListBoxRow, query: str) -> bool:
        """Return if a Gtk.ListBoxRow with a PatientRow matches a query.

        Args:
            list_box_row (Gtk.ListBoxRow): The Gtk.ListboxRow. Must contain a
                PatientRow
            query (str): The query
        """
        patient: patient_util.Patient = list_box_row.get_child().patient

        ratios: List[int] = []
        patient_string: str = " ".join(
            (str(patient.patient_id), patient.first_name, patient.last_name,)
        )

        words: List[str] = query.split(" ")

        for word in words:
            ratios.append(fuzz.partial_ratio(query, patient_string))

            print(query, ":", word, ":", patient_string, ":", ratios[-1])

        return max(ratios) > 80

    def on_info_clicked(self, button: Gtk.Button) -> None:
        """React to the row's info button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page("edit_patient", patient=self.patient)


class PatientHeader(Gtk.Box):
    """A widget that acts as a header for PatientRow widgets."""

    def __init__(self):
        """Create a new PatientRow.

        Args:
            patient (patient_util.Patient): The patient to represent

        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_margin_start(2)
        self.set_margin_end(2)

        for column in patient_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = COLUMN_HEADER_TRANSLATIONS[column]

            cell_label = Gtk.Label(label=text)

            cell_label.set_size_request(-1, 32)
            cell_label.set_halign(Gtk.Align.START)
            cell_label.set_margin_start(4)
            cell_label.set_xalign(0)

            size_groups[column].add_widget(cell_label)

            self.pack_start(cell_label, expand=True, fill=True, padding=4)

            self.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                expand=False,
                fill=False,
                padding=4,
            )

        if size_groups.get("INFO_BUTTON", None) is None:
            size_groups["INFO_BUTTON"] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

        info_button_placeholder: Gtk.Button = Gtk.Box()
        info_button_placeholder.set_size_request(40, 40)
        info_button_placeholder.set_border_width(2)

        size_groups["INFO_BUTTON"].add_widget(info_button_placeholder)

        self.pack_start(
            info_button_placeholder, expand=False, fill=False, padding=4
        )

        self.show_all()
