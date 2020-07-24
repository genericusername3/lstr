"""A page that prompts the user to view, edit or create a program."""

from typing import Union, Optional, Dict

from decimal import Decimal, InvalidOperation

from gi.repository import GObject, Gdk, Gtk  # type: ignore

from .page import Page, PageClass

from . import program_util
from . import auth_util


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/edit_program_page.ui"
)
class EditProgramPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to view, edit or create a program.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "EditProgramPage"

    header_visible: bool = True
    title: str = "Neues Programm"

    program: Optional[program_util.Program] = None

    angle_change_down_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    angle_change_up_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    distance_correction_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    distance_correction_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    distance_correction_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    distance_correction_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    move_distance_down_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    move_distance_up_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pass_count_down_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pass_count_up_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pass_count_total_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    push_count_down_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    push_count_up_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pusher_delay_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_delay_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_delay_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_delay_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pusher_distance_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_distance_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_distance_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_distance_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pusher_move_count_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_move_count_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_move_count_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_move_count_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pusher_speed_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_speed_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_speed_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_speed_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    pusher_stay_down_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_stay_down_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_stay_up_left_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pusher_stay_up_right_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    save_box: Union[Gtk.Box, Gtk.Template.Child] = Gtk.Template.Child()
    delete_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    save_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    save_new_button: Union[
        Gtk.Button, Gtk.Template.Child
    ] = Gtk.Template.Child()

    editable: bool = False

    def __init__(self, **kwargs):
        """Create a new EditProgramPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, program: Optional[program_util.Program] = None) -> None:
        """Prepare the page to be shown."""
        self.program = program

        if program is None:
            self.title = "Neues Programm"
            for entry in self.entries:
                entry.set_text("")
        else:
            self.title = f"Programm {program.id}"
            for entry in self.entries:
                entry.set_text(str(program[self.entries[entry]["column"]]))

        self.editable = True

        self.update_save_sensitivities()

        is_admin: bool = (
            self.get_toplevel().active_user is not None
            and auth_util.get_access_level(self.get_toplevel().active_user)
            == "admin"
        )

        for entry in self.entries:
            entry.set_sensitive(is_admin)

        self.save_box.set_visible(is_admin)

    def unprepare(self) -> None:
        """Prepare the page to be hidden."""
        self.editable = False

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.entries: Dict[
            Gtk.Entry, Dict[str, Union[str, int, Optional[float], bool]]
        ] = {
            self.angle_change_down_entry: {
                "column": "angle_change_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.angle_change_up_entry: {
                "column": "angle_change_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.distance_correction_down_left_entry: {
                "column": "pusher_left_distance_correction_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.distance_correction_down_right_entry: {
                "column": "pusher_right_distance_correction_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.distance_correction_up_left_entry: {
                "column": "pusher_left_distance_correction_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.distance_correction_up_right_entry: {
                "column": "pusher_right_distance_correction_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.move_distance_down_entry: {
                "column": "push_distance_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.move_distance_up_entry: {
                "column": "push_distance_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pass_count_down_entry: {
                "column": "pass_count_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pass_count_total_entry: {
                "column": "pass_count_sum",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": True,
            },
            self.pass_count_up_entry: {
                "column": "pass_count_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.push_count_down_entry: {
                "column": "push_count_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.push_count_up_entry: {
                "column": "push_count_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_delay_down_left_entry: {
                "column": "pusher_left_delay_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_delay_down_right_entry: {
                "column": "pusher_right_delay_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_delay_up_left_entry: {
                "column": "pusher_left_delay_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_delay_up_right_entry: {
                "column": "pusher_right_delay_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_distance_down_left_entry: {
                "column": "pusher_left_distance_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_distance_down_right_entry: {
                "column": "pusher_right_distance_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_distance_up_left_entry: {
                "column": "pusher_left_distance_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_distance_up_right_entry: {
                "column": "pusher_right_distance_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_move_count_down_left_entry: {
                "column": "pusher_left_push_count_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_move_count_down_right_entry: {
                "column": "pusher_right_push_count_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_move_count_up_left_entry: {
                "column": "pusher_left_push_count_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_move_count_up_right_entry: {
                "column": "pusher_right_push_count_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_speed_down_left_entry: {
                "column": "pusher_left_speed_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_speed_down_right_entry: {
                "column": "pusher_right_speed_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_speed_up_left_entry: {
                "column": "pusher_left_speed_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_speed_up_right_entry: {
                "column": "pusher_right_speed_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_stay_down_left_entry: {
                "column": "pusher_left_stay_duration_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_stay_down_right_entry: {
                "column": "pusher_right_stay_duration_down",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_stay_up_left_entry: {
                "column": "pusher_left_stay_duration_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
            self.pusher_stay_up_right_entry: {
                "column": "pusher_right_stay_duration_up",
                "places": 0,
                "leading_zeroes": 0,
                "minimum": None,
                "maximum": None,
                "calculated_column": False,
            },
        }

        for entry in self.entries:
            places: int = self.entries[entry]["places"]
            leading_zeroes: int = self.entries[entry]["leading_zeroes"]

            minimum: Optional[Union[int, float, Decimal]] = (
                self.entries[entry]["minimum"]
            )
            maximum: Optional[Union[int, float, Decimal]] = (
                self.entries[entry]["maximum"]
            )

            entry.connect("focus-in-event", self.on_focus_entry)
            entry.connect(
                "focus-out-event",
                self.on_unfocus_num_entry,
                leading_zeroes,
                places,
                minimum,
                maximum,
            )
            entry.connect(
                "insert-text",
                self.on_num_entry_insert,
                places,
                minimum,
                maximum,
            )

            entry.connect_after("changed", self.on_after_entry_changed)

        self.delete_button.connect("clicked", self.on_delete_clicked)
        self.save_button.connect("clicked", self.on_save_clicked)
        self.save_new_button.connect("clicked", self.on_save_new_clicked)

    def on_num_entry_insert(
        self,
        editable: Gtk.Editable,
        new_text: str,
        new_text_length: int,
        position: int,
        digits: int = 0,
        minimum: Optional[Union[int, float, Decimal]] = None,
        maximum: Optional[Union[int, float, Decimal]] = None,
    ):
        """React to insertion into a Gtk.Editable and only allow numbers.

        Args:
            editable (Gtk.Editable): The Gtk.Editable that received the signal
            new_text (str): The new text to insert
            new_text_length (int): The length of the new text, in bytes, or -1
                if new_text is nul-terminated
            position (int): The position, in characters, at which to insert the
                new text.
            digits (int, optional): How many digits to allow after a decimal
                point (comma). 0 to disallow decimal points. Defaults to 0
        """
        old_text: str = editable.get_text()
        cursor_pos: int = editable.get_position()
        if self.editable:
            if cursor_pos == 0 and (minimum is None or minimum < 0):
                new_text = new_text[0].replace("-", "") + new_text[1:]

            if digits > 0:
                if cursor_pos > 0:
                    new_text = new_text.replace(",", "")
                else:
                    new_text = new_text[0] + new_text[1:].replace(",", "")

            if new_text != "" and not str.isnumeric(new_text):
                GObject.signal_stop_emission_by_name(editable, "insert-text")

            elif "," in old_text and cursor_pos - old_text.index(",") > digits:
                GObject.signal_stop_emission_by_name(editable, "insert-text")

    def on_unfocus_num_entry(
        self,
        entry: Gtk.Entry,
        event: Gdk.EventFocus,
        leading_zeroes: int = 0,
        places: int = 0,
        minimum: Optional[Union[int, float, Decimal]] = None,
        maximum: Optional[Union[int, float, Decimal]] = None,
    ) -> None:
        """React to an entry being unfocused.

        This hides the on-screen keyboard, inserts leading zeroes, ensures the
            number is within a given range and inserts omitted year digits.

        Args:
            entry (Gtk.Entry): The focused entry.
            event (Gdk.EventFocus): The focus event.
            leading_zeroes (int, optional): Up to which length to insert
                leading zeroes.
                E.g. leading_zeroes=4, entry_text="75" -> "0075"
            minimum (Union[Callable[..., Number], Number], optional): The
                minimum value of the text or a function that returns the
                minimum/maximum value. Defaults to None
            maximum (Union[Callable[..., Number], Number], optional): The
                maximum value of the text or a function that returns the
                minimum/maximum value. Defaults to None
            year (bool, optional): Whether the number is a year
        """
        if self.editable:
            self.on_unfocus_entry(entry, event)

            self.check_input(
                entry, leading_zeroes, places, minimum, maximum,
            )

    def check_input(
        self,
        entry: Gtk.Entry,
        leading_zeroes: int = 0,
        places: int = 0,
        minimum: Optional[Union[int, float, Decimal]] = None,
        maximum: Optional[Union[int, float, Decimal]] = None,
    ):
        """Validate the entry text.

        This inserts leading zeroes, ensures the number is within a given
            range and inserts omitted year digits.

        Args:
            entry (Gtk.Entry): The focused entry.
            event (Gdk.EventFocus): The focus event.
            leading_zeroes (int, optional): Up to which length to insert
                leading zeroes.
                E.g. leading_zeroes=4, entry_text="75" -> "0075"
            minimum (Union[Callable[..., Number], Number], optional): The
                minimum value of the text or a function that returns the
                minimum/maximum value. Defaults to None
            maximum (Union[Callable[..., Number], Number], optional): The
                maximum value of the text or a function that returns the
                minimum/maximum value. Defaults to None
            year (bool, optional): Whether the number is a year
        """
        if self.editable:
            text: str = entry.get_text()

            if text == "":
                return

            text = text.replace(",", ".").zfill(1)

            value: Union[int, Decimal]

            if places > 0:
                value = Decimal(text)
                q: Decimal = Decimal(10) ** -places

                if minimum is not None:
                    value = max(value, Decimal(minimum))
                if maximum is not None:
                    value = min(value, Decimal(maximum))

                value = value.quantize(q)

                entry.set_text(
                    str(value).replace(".", ",").zfill(leading_zeroes + 2)
                )

            else:  # Int
                value = int(text)

                if minimum is not None:
                    value = int(max(value, minimum))
                if maximum is not None:
                    value = int(min(value, maximum))

                entry.set_text(format(int(value), f"0{leading_zeroes}d"))

    def on_after_entry_changed(self, entry: Gtk.Entry) -> None:
        """React to an entry being changed after other handlers have run.

        Args:
            entry (Gtk.Entry): The unfocused Gtk.Entry
        """
        if self.editable:
            try:
                self.pass_count_total_entry.set_text(
                    str(
                        Decimal(self.pass_count_up_entry.get_text())
                        + Decimal(self.pass_count_down_entry.get_text())
                    )
                )
            except InvalidOperation:
                pass

            self.update_save_sensitivities()

    def update_save_sensitivities(self) -> None:
        """Update the sensitivity of the save buttons.

        Updates according to input values and active program
        """
        self.save_new_button.set_sensitive(True)
        self.save_button.set_sensitive(True)

        if self.program is None:
            self.save_button.set_sensitive(False)

        for entry in self.entries:
            try:
                float(entry.get_text())  # Raises a ValueError for invalid text
            except ValueError:
                self.save_new_button.set_sensitive(False)
                self.save_button.set_sensitive(False)
                break

    def on_delete_clicked(self, button: Gtk.Button) -> None:
        """React to the "Delete" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        assert self.program is not None

        dialog = Gtk.MessageDialog(
            self.get_toplevel(),
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            ("Nein", Gtk.ResponseType.NO, "Ja", Gtk.ResponseType.YES),
            (f"Programm {self.program.id} unwiderruflich löschen?"),
        )
        dialog.set_decorated(False)
        response: int = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.program.delete()
            self.get_toplevel().go_back()

        elif response == Gtk.ResponseType.NO:
            pass

    def on_save_clicked(self, button: Gtk.Button) -> None:
        """React to the user clicking on the "Save" button.

        Args:
            button (Gtk.Button): The clicked button
        """
        assert self.program is not None

        self.program.modify(
            **{
                self.entries[entry]["column"]: float(
                    entry.get_text().replace(",", ".")
                )
                for entry in self.entries
                if not self.entries[entry]["calculated_column"]
            }
        )

    def on_save_new_clicked(self, button: Gtk.Button) -> None:
        """React to the user clicking on the "Save as new" button.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.program = program_util.Program.add(
            {
                self.entries[entry]["column"]: program_util.PROGRAM_COLUMNS[
                    self.entries[entry]["column"]
                ][0](float(entry.get_text().replace(",", ".")))
                for entry in self.entries
                if not self.entries[entry]["calculated_column"]
            }
        )

        self.title = f"Programm {self.program.id}"
        self.get_toplevel().update_title()

        self.update_save_sensitivities()


# Make EditProgramPage accessible via .ui files
GObject.type_ensure(EditProgramPage)
