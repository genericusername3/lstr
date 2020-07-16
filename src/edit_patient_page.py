"""A page that prompts the user to select a patient."""

from typing import Union, Optional, Callable, List
from numbers import Number

from math import modf
from datetime import date

from gi.repository import GObject, Gdk, Gtk  # type: ignore

from .page import Page, PageClass

from . import patient_util


today_year: int = date.today().year
today_century: int = int(today_year / 100) * 100

MONTHS = {
    1: 31,
    2: 28,  # February is calculated separately
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/edit_patient_page.ui"
)
class EditPatientPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to view, edit or create a patient.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        is_patient_info_page (bool): whether the Page shows one patient's info,
            i.e. a Page with this set to True will not have a patient button in
            the header bar
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "EditPatientPage"

    header_visible: bool = True
    title: str = "Patient hinzufügen"
    is_patient_info_page: bool = True

    patient: Optional[patient_util.Patient] = None

    first_name_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    last_name_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    gender_combobox_text: Union[
        Gtk.ComboBoxText, Gtk.Template.Child
    ] = Gtk.Template.Child()

    birth_date_day_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    birth_date_month_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()
    birth_date_year_entry: Union[
        Gtk.Entry, Gtk.Template.Child
    ] = Gtk.Template.Child()

    weight_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    comment_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

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

            self.first_name_entry.set_text(patient.first_name)
            self.last_name_entry.set_text(patient.last_name)

            if not self.gender_combobox_text.set_active_id(patient.gender):
                self.gender_combobox_text.set_active_id(None)

            (
                birth_date_year,
                birth_date_month,
                birth_date_day,
            ) = patient.birthday.split("-")  # Thank god for ISO 8601

            self.birth_date_day_entry.set_text(birth_date_day)
            self.birth_date_month_entry.set_text(birth_date_month)
            self.birth_date_year_entry.set_text(birth_date_year)


            print(patient.weight)
            self.weight_entry.set_text(str(patient.weight).replace(".", ","))

            self.comment_entry.set_text(patient.comment)

        else:
            self.title = "Patient hinzufügen"

            self.first_name_entry.set_text("")
            self.last_name_entry.set_text("")

            self.gender_combobox_text.set_active_id(None)

            self.birth_date_day_entry.set_text("")
            self.birth_date_month_entry.set_text("")
            self.birth_date_year_entry.set_text("")

            self.weight_entry.set_text("")

            self.comment_entry.set_text("")

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        # Name entries
        self.first_name_entry.connect("focus-in-event", self.on_focus_entry)
        self.first_name_entry.connect("focus-out-event", self.on_unfocus_entry)
        self.last_name_entry.connect("focus-in-event", self.on_focus_entry)
        self.last_name_entry.connect("focus-out-event", self.on_unfocus_entry)

        # Day entry
        self.birth_date_day_entry.connect(
            "focus-in-event", self.on_focus_entry
        )
        self.birth_date_day_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 1, self.max_day,
        )
        self.birth_date_day_entry.connect(
            "insert-text", self.on_num_entry_insert
        )

        # Month entry
        self.birth_date_month_entry.connect(
            "focus-in-event", self.on_focus_entry
        )
        self.birth_date_month_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 1, 12
        )
        self.birth_date_month_entry.connect(
            "insert-text", self.on_num_entry_insert
        )

        # Year entry
        self.birth_date_year_entry.connect(
            "focus-in-event", self.on_focus_entry
        )
        self.birth_date_year_entry.connect(
            "focus-out-event",
            self.on_unfocus_num_entry,
            4,
            today_year - 100,
            today_year,
            True,
        )
        self.birth_date_year_entry.connect(
            "insert-text", self.on_num_entry_insert
        )

        # Weight entry
        self.weight_entry.connect("focus-in-event", self.on_focus_entry)
        self.weight_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 0, 999.9
        )
        self.weight_entry.connect("insert-text", self.on_num_entry_insert, 1)

        # Comment entry
        self.comment_entry.connect("focus-in-event", self.on_focus_entry)
        self.comment_entry.connect("focus-out-event", self.on_unfocus_entry)

        # Entries that are date input
        self.date_entries: List[Gtk.Entry] = [
            self.birth_date_day_entry,
            self.birth_date_month_entry,
            self.birth_date_year_entry,
        ]

    def on_num_entry_insert(
        self,
        editable: Gtk.Editable,
        new_text: str,
        new_text_length: int,
        position: int,
        digits: int = 0,
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

        if digits > 0:
            if cursor_pos > 0:
                new_text = new_text.replace(",", "")
            else:
                new_text = new_text[0] + new_text[1:].replace(",", "")


        if new_text != "" and not str.isnumeric(new_text):
            GObject.signal_stop_emission_by_name(editable, "insert-text")
            print("prevented insert of:", new_text)

        elif "," in old_text and cursor_pos - old_text.index(",") > digits:
            GObject.signal_stop_emission_by_name(editable, "insert-text")
            print("prevented insert of:", new_text)

    def on_unfocus_num_entry(
        self,
        entry: Gtk.Entry,
        event: Gdk.EventFocus,
        leading_zeroes: int = 0,
        minimum: Optional[Union[Callable[..., Number], Number]] = None,
        maximum: Optional[Union[Callable[..., Number], Number]] = None,
        year: bool = False,
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
        self.on_unfocus_entry(entry, event)

        if callable(minimum):
            minimum = minimum()
        if callable(maximum):
            maximum = maximum()

        text: str = entry.get_text()

        if text == "":
            return

        text = "0" + text.replace(",", ".")

        value: Union[int, float]

        print(text, leading_zeroes, year)

        if "." in text:  # Float
            value = float(text)

            if minimum is not None:
                value = max(value, minimum)
            if maximum is not None:
                value = min(value, maximum)

            frac, whole = modf(value)
            entry.set_text(
                format(int(whole), f"0{leading_zeroes}d")
                + str(frac).replace("0", "", 1)
            )

        else:  # Int
            value = int(text)

            if year:
                # Re-include digits of the year e.g. (19)73
                if value < 100 and leading_zeroes > 2:
                    if today_century + value > today_year:
                        value += today_century - 150
                    else:
                        value += today_century

            if minimum is not None:
                value = int(max(value, minimum))
            if maximum is not None:
                value = int(min(value, maximum))

            entry.set_text(format(int(value), f"0{leading_zeroes}d"))

        if entry in self.date_entries:
            self.on_date_changed()

    def on_date_changed(self):
        """React to the user editing the date.

        This exists to account for the user changing between months
            or leap and non-leap years
        """
        day_text: str = self.birth_date_day_entry.get_text()
        if day_text != "":
            self.birth_date_day_entry.set_text(
                str(min(int(day_text), self.max_day()))
            )

    def max_day(self) -> int:
        """Return the most fitting maximum day number.

        This takes the values that have already been input into month and year
        fields into account
        """
        month: int = min(int(self.birth_date_month_entry.get_text() or 1), 12)
        year: int = int(self.birth_date_year_entry.get_text() or 1)

        if month != 2:
            return MONTHS[month]
        elif year % 400:
            return MONTHS[month] + 1  # Leap year
        elif year % 100:
            return MONTHS[month]  # No leap year
        elif year % 4:
            return MONTHS[month] + 1  # Leap year
        else:
            return MONTHS[month]  # No leap year


# Make EditPatientPage accessible via .ui files
GObject.type_ensure(EditPatientPage)
