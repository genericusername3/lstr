"""A widget that represents one patient in horizontal orientation.

Ideal for viewing patients in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, Optional

from datetime import datetime

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
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

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

            self.pack_start(cell_label, expand=True, fill=True, padding=4)

            self.pack_start(
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
        info_button.set_size_request(40, 40)
        info_button.set_border_width(2)

        size_groups["INFO_BUTTON"].add_widget(info_button)

        self.pack_start(info_button, expand=False, fill=False, padding=4)

        self.show_all()


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

        info_button_placeholder: Gtk.Button = Gtk.Box()
        info_button_placeholder.set_size_request(40, 40)
        info_button_placeholder.set_border_width(2)

        size_groups["INFO_BUTTON"].add_widget(info_button_placeholder)

        self.pack_start(
            info_button_placeholder, expand=False, fill=False, padding=4
        )

        self.show_all()


def header_func(row: Gtk.ListBoxRow, before: Optional[Gtk.ListBoxRow]):
    if before is None:
        row.set_header(PatientHeader())
