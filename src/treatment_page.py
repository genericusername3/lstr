"""A page that allows the user to perform a treatment program on a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from .program_util import Program
from .opcua_util import Connection


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/treatment_page.ui"
)
class TreatmentPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that allows the user to perform a treatment program on a patient.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "TreatmentPage"

    header_visible: bool = True
    title: str = "Behandlung"

    # %%WIDGET_NAME%%: Union[Gtk.Widget, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new TreatmentPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self) -> None:
        """Prepare the page to be shown."""
        program: Program = self.get_toplevel().active_program
        for key in Connection()["program"].keys():
            print(program[key])

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


# Make TreatmentPage accessible via .ui files
GObject.type_ensure(TreatmentPage)
