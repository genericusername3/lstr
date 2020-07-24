"""A widget that represents one treatment entry in horizontal orientation.

Ideal for viewing treatments in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, Union, Set

from gi.repository import GLib, Gtk  # type: ignore

from .page import Page

from . import treatment_util


size_groups: Dict[str, Gtk.SizeGroup] = {}

COLUMN_HEADER_TRANSLATIONS: Dict[str, str] = {
    "date": "Datum",
    "program_id": "Programm",
    "pain_location": "Schmerzen",
    "pain_intensity": "VAS",
    "username": "Behandelnder Benutzer",
}

MONOSPACE_COLUMNS: Set[str] = {"date"}

VALUE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "pain_location": {
        "left": "Links",
        "left-right": "Eher links",
        "both": "Beidseitig",
        "right-left": "Eher rechts",
        "right": "Rechts",
    }
}


class TreatmentRow(Gtk.Box):
    """A widget that represents one user in horizontal orientation.

    Ideal for viewing users in lists, because all columns are added to a
        Gtk.SizeGroup

    This widget contains a button that offers the user to view more information
        about the user and edit user data.
    """

    user: treatment_util.Treatment

    def __init__(self, treatment: treatment_util.Treatment):
        """Create a new TreatmentRow.

        Args:
            treatment (treatment_util.Treatment): The treatment to represent
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.treatment = treatment

        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.pack_start(h_box, expand=True, fill=True, padding=0)

        self.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            expand=True,
            fill=True,
            padding=0,
        )

        for column in treatment_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            if treatment.__dict__.get(column) is not None:
                text = GLib.markup_escape_text(str(treatment.__dict__.get(column)))
            else:
                text = "-"

            # Get a translation if available
            text = VALUE_TRANSLATIONS.get(column, {}).get(text, text)

            if column in MONOSPACE_COLUMNS:
                text = f"<tt>{text}</tt>"

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

        self.show_all()


class TreatmentHeader(Gtk.Box):
    """A widget that acts as a header for TreatmentRow widgets."""

    def __init__(self):
        """Create a new TreatmentHeader."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_margin_start(2)
        self.set_margin_end(2)

        for column in treatment_util.DISPLAY_COLUMNS:
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

        self.show_all()
