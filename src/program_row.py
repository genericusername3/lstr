"""A widget that represents one program in horizontal orientation.

Ideal for viewing programs in lists, because all columns are added to a
Gtk.SizeGroup
"""

from typing import Dict, Union

from gi.repository import GLib, Gtk  # type: ignore

from . import program_util


size_groups: Dict[str, Gtk.SizeGroup] = {}

COLUMN_HEADER_TRANSLATIONS: Dict[str, str] = {
    "id": "Nr.",
    "pusher_left_distance_max": "Pusherstrecke L",
    "pusher_right_distance_max": "Pusherstrecke R",
    "push_count_sum": "Anzahl Vorschübe",
    "pass_count_sum": "Anzahl Durchläufe",
}

INFO_ICON = "view-more-horizontal-symbolic"
WARNING_ICON = "dialog-warning-symbolic"


class ProgramRow(Gtk.Box):
    """A widget that represents one program in horizontal orientation.

    Ideal for viewing programs in lists, because all columns are added to a
        Gtk.SizeGroup

    This widget contains a button that offers the user to view more information
        about the program and edit program data.
    """

    program: program_util.Program

    def __init__(
        self,
        program: program_util.Program,
    ):
        """Create a new ProgramRow.

        Args:
            program (program_util.Program): The program to represent

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

        self.program = program

        for column in program_util.DISPLAY_COLUMNS:
            if size_groups.get(column, None) is None:
                size_groups[column] = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)

            text = GLib.markup_escape_text(str(program[column]))

            if column in program_util.UNIT_COLUMNS:
                text = text + " " + program_util.UNIT_COLUMNS[column]

            cell_label = Gtk.Label(label=text)

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

        # Info button
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

    def on_info_clicked(self, button: Gtk.Button) -> None:
        """React to the row's info button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page("edit_program", program=self.program)


class ProgramHeader(Gtk.Box):
    """A widget that acts as a header for ProgramRow widgets."""

    def __init__(self):
        """Create a new ProgramRow.

        Args:
            program (program_util.Program): The program to represent

        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_margin_start(2)
        self.set_margin_end(2)

        for column in program_util.DISPLAY_COLUMNS:
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

        # Info button
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
