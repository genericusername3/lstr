"""A page that prompts the user to input the patient's pain values."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/pain_evaluation_page.ui"
)
class PainEvaluationPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to input the patient's pain values.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        pain_entry_time (Optional[int]): The timestamp of the pain entry
            (only available after confirming)
        pain_scale (Gtk.Scale or Gtk.Template.Child): A Gtk.Scale for pain
            intensity (0-10)
        pain_location_combobox_text (Gtk.ComboBoxText or Gtk.Template.Child): A
            Gtk.ComboBoxText that offers the following options:
                left
                left-right
                both
                right-left
                right
        save_button (Gtk.Button or Gtk.Template.Child): The button that saves
            the pain entry
    """

    __gtype_name__ = "PainEvaluationPage"

    header_visible: bool = True
    title: str = "Schmerzen erfassen"

    pain_scale: Union[
        Gtk.Scale, Gtk.Template.Child
    ] = Gtk.Template.Child()
    pain_location_combobox_text: Union[
        Gtk.ComboBoxText, Gtk.Template.Child
    ] = Gtk.Template.Child()

    save_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    pain_entry_time: Optional[int] = None

    def __init__(self, **kwargs):
        """Create a new PainEvaluationPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        self.get_toplevel().treatment_timestamp = None

        self.pain_entry_time = None

        self.pain_scale.set_value(0)

        self.pain_location_combobox_text.set_active_id(None)

        self.save_button.set_sensitive(False)

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.save_button.connect("clicked", self.on_save_clicked)

        self.pain_location_combobox_text.connect("changed", self.on_pain_location_changed)

    def on_pain_location_changed(self, combobox: Gtk.ComboBox):
        """React to the selection of the pain location changing.

        Args:
            combobox (Gtk.ComboBox): The pain location combobox
        """
        self.save_button.set_sensitive(True)


    def on_save_clicked(self, button: Gtk.Button) -> None:
        """React to the save button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        window: Gtk.Window = self.get_toplevel()

        if window.treatment_timestamp is None:
            window.treatment_timestamp = window.active_patient.add_pain_entry(
                window.active_user,
                self.pain_scale.get_value(),
                self.pain_location_combobox_text.get_active_id(),
            )
        else:
            window.treatment_timestamp = window.active_patient.modify_pain_entry(
                window.treatment_timestamp,
                window.active_user,
                self.pain_scale.get_value(),
                self.pain_location_combobox_text.get_active_id(),
            )

        window.switch_page("setup")


# Make PainEvaluationPage accessible via .ui files
GObject.type_ensure(PainEvaluationPage)
