"""A page that prompts the user to select a program."""

from typing import Union, Optional

from gi.repository import GObject, Gtk  # type: ignore

from .page import Page, PageClass

from . import auth_util

from .program_util import Program
from .program_row import ProgramRow, ProgramHeader


@Gtk.Template(
    resource_path="/de/linusmathieu/Liegensteuerung/select_program_page.ui"
)
class SelectProgramPage(Gtk.Box, Page, metaclass=PageClass):
    """A page that prompts the user to select a program.

    Attributes:
        header_visible (bool): Whether a Gtk.HeaderBar should be shown for the
            page
        title (str): The Page's title
        %%Wigdet_NAME%% (Gtk.Entry or Gtk.Template.Child): The entry for the
            user's username
    """

    __gtype_name__ = "SelectProgramPage"

    header_visible: bool = True
    title: str = "Programm auswählen"

    program_list_box: Union[
        Gtk.ListBox, Gtk.Template.Child
    ] = Gtk.Template.Child()

    header_box: Union[Gtk.Box, Gtk.Template.Child] = Gtk.Template.Child()

    add_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    end_pos_left_label: Union[
        Gtk.Label, Gtk.Template.Child
    ] = Gtk.Template.Child()
    end_pos_right_label: Union[
        Gtk.Label, Gtk.Template.Child
    ] = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create a new SelectProgramPage.

        Args:
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

    def prepare(self, max_left: int, max_right: int) -> None:
        """Prepare the page to be shown.

        Args:
            max_left (int): The maximum pusher_left_distance_up to allow
            max_right (int): The maximum pusher_right_distance_up to allow
        """
        self.end_pos_left_label.set_text(f"{max_left} mm")
        self.end_pos_right_label.set_text(f"{max_right} mm")

        self.max_left, self.max_right = max_left, max_right

        self.update_programs()

        is_admin: bool = (
            self.get_toplevel().active_user is not None
            and auth_util.get_access_level(self.get_toplevel().active_user)
            == "admin"
        )

        self.add_button.set_visible(is_admin)

    def prepare_return(self) -> None:
        """Prepare the page to be shown when returning from another page."""
        self.get_toplevel().active_program = None

        # Inefficient to re-load all programs, but everything else is more work
        self.update_programs()

    def update_programs(self) -> None:
        """Re-query all programs."""
        self.program_list_box.bind_model(
            Program.iter_to_model(
                Program.get_fitting(self.max_left, self.max_right)
            ),
            ProgramRow,
        )
        self.program_list_box.show_all()

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        self.header_box.pack_start(
            ProgramHeader(), fill=True, expand=True, padding=0
        )
        self.header_box.show_all()

        self.program_list_box.connect("row-selected", self.on_program_selected)

        self.add_button.connect("clicked", self.on_add_clicked)

    def on_program_selected(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow):
        """React to the user selecting a program.

        This will switch to the page 'pain_evaluation'.

        Args:
            list_box (Gtk.ListBox): The Gtk.ListBox that is the row's parent
            row (Gtk.ListBoxRow): The Gtk.ListBoxRow that was selected
        """
        if row is not None:
            self.get_toplevel().active_program = row.get_child().program

            self.get_toplevel().switch_page("treatment")
        list_box.unselect_all()

    def on_add_clicked(self, button: Gtk.Button) -> None:
        """React to the "add program" button being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        self.get_toplevel().switch_page("edit_program")


# Make SelectProgramPage accessible via .ui files
GObject.type_ensure(SelectProgramPage)
