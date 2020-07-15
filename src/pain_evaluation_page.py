"""A page that prompts the user to select a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/pain_evaluation_page.ui"
)
class PainEvaluationPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to enter two levels of pain.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        left_pain_scale (Gtk.Scale or Gtk.Template.Child): The scale for the
            left-sided pain
        right_pain_scale (Gtk.Scale or Gtk.Template.Child): The scale for the
            right-sided pain
        save_button (Gtk.Button or Gtk.Template.Child): The button that saves
            the pain entry
    """

    __gtype_name__ = "PainEvaluationPage"

    header_visible: bool = True
    title: str = "Schmerzen erfassen"

    left_pain_scale: Union[
        Gtk.Scale, Gtk.Template.Child
    ] = Gtk.Template.Child()
    right_pain_scale: Union[
        Gtk.Scale, Gtk.Template.Child
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
        self.pain_entry_time = None

        self.left_pain_scale.set_value(0)
        self.right_pain_scale.set_value(0)

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

    def on_save_clicked(self, button: Gtk.Button) -> None:
        """React to the save button being clicked.

        Args:
            button (Gtk.Button): The button that was clicked
        """
        window: Gtk.Window = self.get_toplevel()

        if self.pain_entry_time is None:
            self.pain_entry_time = window.active_patient.add_pain_entry(
                self.left_pain_scale.get_value(),
                self.right_pain_scale.get_value(),
            )
        else:
            self.pain_entry_time = window.active_patient.modify_pain_entry(
                self.pain_entry_time,
                self.left_pain_scale.get_value(),
                self.right_pain_scale.get_value(),
            )

        window.switch_page("setup")


# Make PainEvaluationPage accessible via .ui files
GObject.type_ensure(PainEvaluationPage)
