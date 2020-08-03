"""A page that prompts the user to view, edit or create a patient."""

from typing import Union, Optional, Callable, List, Tuple
from numbers import Number
from decimal import Decimal

from datetime import date

from gi.repository import GObject, GLib, Gdk, Gtk  # type: ignore

from .page import Page, PageClass

from . import auth_util
from . import patient_util

from .treatment_util import Treatment
from .treatment_row import TreatmentRow, TreatmentHeader


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


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/edit_patient_page.ui")
class EditPatientPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to view, edit or create a patient.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        is_patient_info_page (bool): whether the Page shows one patient's info,
            i.e. a Page with this set to True will not have a patient button in
            the header bar
        title (str): The Page's title

        first_name_entry (Union[Gtk.Entry, Gtk.Template.Child]) A Gtk.Entry for
            the patient's first name
        last_name_entry (Union[Gtk.Entry, Gtk.Template.Child]) A Gtk.Entry for
            the patient's last name

        gender_combobox_text (Union[Gtk.ComboBoxText, Gtk.Template.Child]) A
            Gtk.ComboBoxText for the patient's gender

        birth_date_day_entry (Union[Gtk.Entry, Gtk.Template.Child]) A Gtk.Entry
            for the patient's birth date day
        birth_date_month_entry (Union[Gtk.Entry, Gtk.Template.Child]) A
            Gtk.Entry for the patient's birth date month
        birth_date_year_entry (Union[Gtk.Entry, Gtk.Template.Child]) A
            Gtk.Entry for the patient's birth date year

        weight_entry (Union[Gtk.Entry, Gtk.Template.Child]) A Gtk.Entry for
            the patient's weight

        comment_entry (Union[Gtk.Entry, Gtk.Template.Child]) A Gtk.Entry for
            a comment on the patient

        editable: bool = Whether the page has set all values and is ready to
            receive and save input
    """

    __gtype_name__ = "EditPatientPage"

    header_visible: bool = True
    title: str = "Patient hinzufügen"
    is_patient_info_page: bool = True

    export_button: Union[Gtk.Template.Child, Gtk.Button] = Gtk.Template.Child()
    export_success_info_bar: Union[
        Gtk.Template.Child, Gtk.InfoBar
    ] = Gtk.Template.Child()

    first_name_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    last_name_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    gender_combobox_text: Union[
        Gtk.ComboBoxText, Gtk.Template.Child
    ] = Gtk.Template.Child()

    birth_date_day_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    birth_date_month_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()
    birth_date_year_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    treatment_list_box: Union[Gtk.ListBox, Gtk.Template.Child] = Gtk.Template.Child()
    header_box: Union[Gtk.Box, Gtk.Template.Child] = Gtk.Template.Child()

    weight_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    comment_entry: Union[Gtk.Entry, Gtk.Template.Child] = Gtk.Template.Child()

    patient_tabs_stack: Union[Gtk.Stack, Gtk.Template.Child] = Gtk.Template.Child()

    patient_tabs_stack_switcher: Union[
        Gtk.StackSwitcher, Gtk.Template.Child
    ] = Gtk.Template.Child()

    delete_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    editable: bool = False

    def __init__(self, **kwargs):
        """Create a new EditPatientPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, patient: Optional[patient_util.Patient] = None) -> None:
        """Prepare the page to be shown."""
        self.patient = patient

        self.patient_tabs_stack.set_visible_child_name("patient")

        self.first_name_entry.grab_focus()

        self.export_success_info_bar.hide()
        self.export_success_info_bar.set_revealed(False)

        if patient is not None:
            self.title = f"{patient.first_name} {patient.last_name}"

            self.first_name_entry.set_text(patient.first_name)
            self.last_name_entry.set_text(patient.last_name)

            if not self.gender_combobox_text.set_active_id(patient.gender):
                self.gender_combobox_text.set_active_id(None)

            # Thank god for ISO 8601
            (
                birth_date_year,
                birth_date_month,
                birth_date_day,
            ) = patient.birthday.split("-")

            self.birth_date_day_entry.set_text(str(birth_date_day))
            self.birth_date_month_entry.set_text(str(birth_date_month))
            self.birth_date_year_entry.set_text(str(birth_date_year))

            self.weight_entry.set_text(str(patient.weight).replace(".", ","))

            self.comment_entry.set_text(patient.comment)

            advanced_access: bool = (
                auth_util.ACCESS_LEVELS[
                    auth_util.get_access_level(self.get_toplevel().active_user)
                ]
                >= 1
            )

            self.delete_button.set_visible(advanced_access)
            self.patient_tabs_stack_switcher.set_visible(advanced_access)

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

            self.delete_button.hide()
            self.patient_tabs_stack_switcher.hide()

        self.editable = True

        self.update_treatments()

    def prepare_return(self):
        """Prepare the page to be shown when returning from another page."""
        self.update_treatments()

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

        self.export_success_info_bar.connect("response", self.on_info_bar_response)

        self.export_button.connect("clicked", self.on_export_clicked)

        # Name entries
        self.first_name_entry.connect("focus-in-event", self.on_focus_entry)
        self.first_name_entry.connect("button-press-event", self.on_entry_button_press)
        self.first_name_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.first_name_entry.connect("focus-out-event", self.on_unfocus_entry)

        self.last_name_entry.connect("focus-in-event", self.on_focus_entry)
        self.last_name_entry.connect("button-press-event", self.on_entry_button_press)
        self.last_name_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.last_name_entry.connect("focus-out-event", self.on_unfocus_entry)

        # Day entry
        self.birth_date_day_entry.connect("focus-in-event", self.on_focus_entry)
        self.birth_date_day_entry.connect(
            "button-press-event", self.on_entry_button_press
        )
        self.birth_date_day_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.birth_date_day_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 1, self.max_day,
        )
        self.birth_date_day_entry.connect("insert-text", self.on_num_entry_insert)

        # Month entry
        self.birth_date_month_entry.connect("focus-in-event", self.on_focus_entry)
        self.birth_date_month_entry.connect(
            "button-press-event", self.on_entry_button_press
        )
        self.birth_date_month_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.birth_date_month_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 1, 12
        )
        self.birth_date_month_entry.connect("insert-text", self.on_num_entry_insert)

        # Year entry
        self.birth_date_year_entry.connect("focus-in-event", self.on_focus_entry)
        self.birth_date_year_entry.connect(
            "button-press-event", self.on_entry_button_press
        )
        self.birth_date_year_entry.connect(
            "button-release-event", self.on_entry_button_release
        )
        self.birth_date_year_entry.connect(
            "focus-out-event",
            self.on_unfocus_num_entry,
            4,
            today_year - 150,
            today_year,
            True,
        )
        self.birth_date_year_entry.connect("insert-text", self.on_num_entry_insert)

        # Weight entry
        self.weight_entry.connect("focus-in-event", self.on_focus_entry)
        self.weight_entry.connect("button-press-event", self.on_entry_button_press)
        self.weight_entry.connect("button-release-event", self.on_entry_button_release)
        self.weight_entry.connect(
            "focus-out-event", self.on_unfocus_num_entry, 2, 0, 999.9
        )
        self.weight_entry.connect("insert-text", self.on_num_entry_insert, 1)

        # Comment entry
        self.comment_entry.connect("focus-in-event", self.on_focus_entry)
        self.comment_entry.connect("button-press-event", self.on_entry_button_press)
        self.comment_entry.connect("button-release-event", self.on_entry_button_release)
        self.comment_entry.connect("focus-out-event", self.on_unfocus_entry)

        # Entries that are date input
        self.date_entries: List[Gtk.Entry] = [
            self.birth_date_day_entry,
            self.birth_date_month_entry,
            self.birth_date_year_entry,
        ]

        self.all_fields: Tuple[Gtk.Entry, ...] = (
            self.first_name_entry,
            self.last_name_entry,
            self.gender_combobox_text,
            self.birth_date_day_entry,
            self.birth_date_month_entry,
            self.birth_date_year_entry,
            self.weight_entry,
            self.comment_entry,
        )

        for field in self.all_fields:
            field.connect_after("changed", self.on_values_changed)

        self.delete_button.connect("clicked", self.on_delete_clicked)

        self.header_box.pack_start(TreatmentHeader(), fill=True, expand=True, padding=0)
        self.header_box.show_all()

    def update_treatments(self) -> None:
        """Re-query all treatments."""
        self.treatment_list_box.bind_model(
            Treatment.iter_to_model(Treatment.get_all()), TreatmentRow,
        )
        self.treatment_list_box.show_all()

        for row in self.treatment_list_box.get_children():
            row.set_activatable(False)

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
        if self.editable:
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
        if self.editable:
            self.on_unfocus_entry(entry, event)

            self.check_input(
                entry, leading_zeroes, minimum, maximum, year,
            )

            if entry in self.date_entries:
                self.on_date_changed(entry)

    def check_input(
        self,
        entry: Gtk.Entry,
        leading_zeroes: int = 0,
        minimum: Optional[Union[Callable[..., Number], Number]] = None,
        maximum: Optional[Union[Callable[..., Number], Number]] = None,
        year: bool = False,
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
            if callable(minimum):
                minimum = minimum()
            if callable(maximum):
                maximum = maximum()

            text: str = entry.get_text()

            if text == "":
                return

            text = text.replace(",", ".").zfill(1)

            value: Union[int, Decimal]

            if "." in text:  # Float
                value = Decimal(text)
                q: Decimal = Decimal(10) ** -1  # 1 place --> '0.1'

                if minimum is not None:
                    value = max(value, Decimal(minimum))
                if maximum is not None:
                    value = min(value, Decimal(maximum))

                value = value.quantize(q)

                entry.set_text(str(value).replace(".", ",").zfill(leading_zeroes + 2))

            else:  # Int
                value = int(text)

                if year:
                    # Re-include digits of the year e.g. (19)73
                    if value < 100 and leading_zeroes > 2:
                        if today_century + value > today_year:
                            value += today_century - 100
                        else:
                            value += today_century

                if minimum is not None:
                    value = int(max(value, minimum))
                if maximum is not None:
                    value = int(min(value, maximum))

                entry.set_text(format(int(value), f"0{leading_zeroes}d"))

    def on_date_changed(self, entry: Gtk.Entry):
        """React to the user editing the date.

        This exists to account for the user changing between months
            or leap and non-leap years

        Args:
            entry (Gtk.Entry): The changed entry.
        """
        if self.editable:
            self.check_input(
                self.birth_date_year_entry, 4, today_year - 150, today_year, True,
            )

            self.check_input(self.birth_date_month_entry, 2, 1, 12)

            self.check_input(self.birth_date_day_entry, 2, 1, self.max_day())

    def max_day(self) -> int:
        """Return the most fitting maximum day number.

        This takes the values that have already been input into month and year
        fields into account
        """
        month: int = min(int(self.birth_date_month_entry.get_text() or 1), 12)
        year: int = int(self.birth_date_year_entry.get_text() or 1)

        if month != 2:
            return MONTHS[month]
        elif year % 400 == 0:
            return MONTHS[month] + 1  # Leap year
        elif year % 100 == 0:
            return MONTHS[month]  # No leap year
        elif year % 4 == 0:
            return MONTHS[month] + 1  # Leap year
        else:
            return MONTHS[month]  # No leap year

    def on_values_changed(self, *args) -> None:
        """React to patient data being changed.

        Args:
            *args: Arguments that Gtk passes to the ::connect handler
        """
        if self.editable:
            if (
                self.first_name_entry.get_text().strip() != ""
                and self.last_name_entry.get_text().strip() != ""
                and self.birth_date_year_entry.get_text() != ""
                and self.birth_date_month_entry.get_text() != ""
                and self.birth_date_day_entry.get_text() != ""
                and self.gender_combobox_text.get_active_id() is not None
                and self.weight_entry.get_text().replace(",", ".") != ""
            ):
                if self.patient is not None:
                    self.patient.modify(
                        first_name=self.first_name_entry.get_text().strip(),
                        last_name=self.last_name_entry.get_text().strip(),
                        birthday=self.birth_date_year_entry.get_text()
                        + "-"
                        + self.birth_date_month_entry.get_text()
                        + "-"
                        + self.birth_date_day_entry.get_text(),
                        gender=self.gender_combobox_text.get_active_id(),
                        weight=float(self.weight_entry.get_text().replace(",", ".")),
                        comment=self.comment_entry.get_text().strip(),
                    )

                else:
                    self.patient = patient_util.Patient.add(
                        first_name=self.first_name_entry.get_text().strip(),
                        last_name=self.last_name_entry.get_text().strip(),
                        birthday=self.birth_date_year_entry.get_text()
                        + "-"
                        + self.birth_date_month_entry.get_text()
                        + "-"
                        + self.birth_date_day_entry.get_text(),
                        gender=self.gender_combobox_text.get_active_id(),
                        weight=float(self.weight_entry.get_text().replace(",", ".")),
                        comment=self.comment_entry.get_text().strip(),
                    )

                    self.title = (
                        f"{self.first_name_entry.get_text()} "
                        f"{self.last_name_entry.get_text()}"
                    )

                    self.get_toplevel().update_title()

            if (
                self.first_name_entry.get_text().strip() != ""
                and self.last_name_entry.get_text().strip() != ""
            ):
                self.title = (
                    f"{self.first_name_entry.get_text().strip()} "
                    f"{self.last_name_entry.get_text().strip()}"
                )

            elif self.patient is None:
                self.title = "Patient hinzufügen"

            else:
                self.title = f"{self.patient.first_name} {self.patient.last_name}"

            self.get_toplevel().update_title()

    def on_delete_clicked(self, button: Gtk.Button) -> None:
        """React to the "Delete" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        assert self.patient is not None

        dialog = Gtk.MessageDialog(
            self.get_toplevel(),
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            ("Nein", Gtk.ResponseType.NO, "Ja", Gtk.ResponseType.YES),
            (
                f"Patient {self.patient.first_name} {self.patient.last_name}"
                " unwiderruflich löschen?"
            ),
        )
        dialog.set_decorated(False)
        response: int = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.patient.delete()
            self.get_toplevel().go_back()
            while self.get_toplevel().active_patient is self.patient:
                self.get_toplevel().go_back()

        elif response == Gtk.ResponseType.NO:
            pass

    def on_export_clicked(self, button: Gtk.Button) -> None:
        """React to the "Export" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        try:
            assert self.patient is not None

            self.patient.simple_export()
            self.export_success_info_bar.set_visible(True)
            self.export_success_info_bar.set_revealed(True)
        except IOError as io_err:
            self.get_toplevel().show_error(" ".join(io_err.args))

    def on_info_bar_response(self, info_bar: Gtk.InfoBar, response: int):
        """React to the user responding to a Gtk.InfoBar.

        Args:
            info_bar (Gtk.InfoBar): The Gtk.InfoBar that received the response
            response (int): The response id (Gtk.ResponseType)
        """
        if response == Gtk.ResponseType.CLOSE:
            info_bar.set_revealed(False)
            GLib.timeout_add(250, info_bar.set_visible, False)


# Make EditPatientPage accessible via .ui files
GObject.type_ensure(EditPatientPage)
