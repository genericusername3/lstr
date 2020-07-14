"""A page that prompts the user to select a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from . import patient_util

from .page import Page, PageClass


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/pain_evaluation_page.ui"
)
class PainEvaluationPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to select a patient.

    Attributes:
        header_visible (bool): whether a Gtk.HeaderBar should be shown for the
            page
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "PainEvaluationPage"

    header_visible: bool = True
    title: str = "Schmerzen erfassen"

    # %%WIDGET_NAME%%: Union[Gtk.Widget, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new PainEvaluationPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, patient: patient_util.Patient) -> None:
        """Prepare the page to be shown."""

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        # Connect events


# Make PainEvaluationPage accessible via .ui files
GObject.type_ensure(PainEvaluationPage)
