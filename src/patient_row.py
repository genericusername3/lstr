"""A widget that represents one patient in horizontal orientation.

Ideal for viewing patients in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, List

from datetime import datetime
from fuzzywuzzy import fuzz  # type: ignore

from gi.repository import GLib, Gdk, Gtk  # type: ignore

from . import patient_util


size_groups: Dict[str, Gtk.SizeGroup] = {}

COLUMN_HEADER_TRANSLATIONS: Dict[str, str] = {
    "patient_id": "Nr.",
    "first_name": "Vorname",
    "last_name": "Nachname",
    "gender_translated": "Geschlecht",
    "birthday": "Geburtsdatum",
}

INFO_ICON = "view-more-horizontal-symbolic"


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

            cell_label.set_size_request(128, 32)
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
            INFO_ICON, Gtk.IconSize.BUTTON
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

    sort_icons: List[Gtk.Image]

    def __init__(self, page):
        """Create a new PatientRow.

        Args:
            page (select_patient_page.SelectPatientPage): The page to act as a
                header for
        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.page = page
        self.sort_icons = []

        self.set_margin_start(2)
        self.set_margin_end(2)

        for col_index, column in enumerate(patient_util.DISPLAY_COLUMNS):
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = COLUMN_HEADER_TRANSLATIONS[column]

            event_box = Gtk.EventBox()

            event_box.connect(
                "button-press-event",
                self.on_column_header_clicked,
                patient_util.COLUMNS.index(
                    column.replace("patient_", "").replace("_translated", "")
                ),
                col_index,
            )

            cell_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=8
            )

            cell_label = Gtk.Label(label=text)

            cell_label.set_size_request(-1, 32)
            cell_label.set_halign(Gtk.Align.START)
            cell_label.set_margin_start(4)
            cell_label.set_xalign(0)

            cell_box.pack_start(
                cell_label, expand=False, fill=False, padding=0
            )

            cell_sort_icon = Gtk.Image()
            self.sort_icons.append(cell_sort_icon)
            # cell_sort_icon.set_no_show_all(True)

            cell_box.pack_end(
                cell_sort_icon, expand=False, fill=False, padding=0
            )

            size_groups[column].add_widget(cell_box)

            event_box.add(cell_box)
            self.pack_start(event_box, expand=True, fill=True, padding=4)

            self.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                expand=False,
                fill=False,
                padding=4,
            )

        if size_groups.get("INFO_BUTTON", None) is None:
            size_groups["INFO_BUTTON"] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

        info_button_dummy: Gtk.Button = Gtk.Box()
        info_button_dummy.set_size_request(40, 40)
        info_button_dummy.set_border_width(2)

        size_groups["INFO_BUTTON"].add_widget(info_button_dummy)

        self.pack_start(
            info_button_dummy, expand=False, fill=False, padding=4
        )

        self.show_all()

        self.update_sort_icons()

    def on_column_header_clicked(
        self,
        event_box: Gtk.EventBox,
        event: Gdk.EventButton,
        column_index: int,
        display_column_index: int,
    ) -> None:
        """React to the user clicking on a column header.

        Sort the listbox by the clicked column and revert if that sort order is
            already being used.

        Args:
            event_box (Gtk.EventBox): The Gtk.EventBox that was clicked
                (pressed) on
            event (Gdk.EventButton): The event that the button press caused
            column_index (int): The column index of the column header
        """
        self.page.set_sort(
            column_index,
            self.page.sort_column == column_index
            and not self.page.sort_reverse,
        )

        self.update_sort_icons()

    def update_sort_icons(self) -> None:
        """Update the sort icons. Hide unnecessary ones, adapt the icons."""
        for image in self.sort_icons:
            image.set_opacity(0.3)
            image.set_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON)

        display_column_index: int = patient_util.DISPLAY_COLUMNS.index(
            patient_util.COLUMNS[self.page.sort_column]
            .replace("id", "patient_id")
            .replace("gender", "gender_translated")
        )

        if self.page.sort_reverse:
            self.sort_icons[display_column_index].set_from_icon_name(
                "go-up-symbolic", Gtk.IconSize.BUTTON
            )

        self.sort_icons[display_column_index].set_opacity(0.9)
