"""A page that prompts the user to select a patient."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from . import program_util


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/edit_program_page.ui"
)
class EditProgramPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to select a patient.

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

    # %%WIDGET_NAME%%: Union[Gtk.Widget, Gtk.Template.Child] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new EditProgramPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, program: Optional[program_util.Program] = None) -> None:
        """Prepare the page to be shown."""
        if program is None:
            self.title = "Neues Programm"
            ...
        else:
            self.title = f"Programm {program.id}"
            ...

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


# Make EditProgramPage accessible via .ui files
GObject.type_ensure(EditProgramPage)
