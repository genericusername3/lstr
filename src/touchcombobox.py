"""An (even simpler) replacement for Gtk.ComboBoxText that is more suitable for touchscreens."""
from typing import Dict, Optional, Union

from gi.repository import GObject, Gtk


class TouchComboBoxItem(Gtk.ListBoxRow):

    """A ListBoxRow with an id containing just a widget.

    Attributes:
        item_id (str): The id
    """

    item_id: str

    def __init__(self, item_id, item_translation):
        super().__init__()

        label: Gtk.Label = Gtk.Label(item_translation)
        label.set_xalign(0)

        label.set_size_request(-1, 36)

        label.set_margin_start(4)
        label.set_margin_end(4)

        self.add(label)

        self.item_id = item_id


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/touchcombobox.ui")
class TouchComboBox(Gtk.Box):
    """An (even simpler) replacement for Gtk.ComboBoxText that is more suitable for touchscreens."""

    __gtype_name__ = "TouchComboBox"

    active_id: Optional[str] = None
    items: Dict[str, str]
    item_widgets: Dict[str, TouchComboBoxItem]

    menu_button: Union[Gtk.Template.Child, Gtk.MenuButton] = Gtk.Template.Child()
    popover: Union[Gtk.Template.Child, Gtk.Popover] = Gtk.Template.Child()
    item_list_box: Union[Gtk.Template.Child, Gtk.ListBox] = Gtk.Template.Child()
    active_label: Union[Gtk.Template.Child, Gtk.Label] = Gtk.Template.Child()

    def __init__(self, items: Dict[str, str] = {}, **kwargs):
        """Create a new TouchComboBox.

        Args:
            items (Dict[str, str], optional): Items the combobox should contain. {<id>: <translation>}
            **kwargs: Keyword arguments passed on to Gtk.Box
        """
        super().__init__(self, **kwargs)

        self.items = dict()
        self.item_widgets = dict()

        for item_id in self.items:
            self.add_item(item_id, self.items[item_id])

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, arg_types=(str,))
    def changed(self, new_id: str) -> None:
        """The changed signal is emitted when the active item is changed.

        Args:
            new_id: The id of the newly selected item
        """
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

        self.item_list_box.connect("row-selected", self.on_item_selected)

    def add_item(self, item_id: str, item_translation: str) -> None:
        """Add an item to the end of the dropdown list.

        Args:
            item_id (str): The ID of the item
            item_translation (str): The translated display text of the item
        """
        self.insert_item(item_id, item_translation, -1)

    def insert_item(self, item_id: str, item_translation: str, position: int) -> None:
        """Add an item to the dropdown list at a specific position.

        Args:
            item_id (str): The ID of the item
            item_translation (str): The translated display text of the item
            position (int): The position at which to insert the item.
                Inserted at the end if this is -1 or larger then the amount
                of items in the dropdown.
        """
        item_widget = TouchComboBoxItem(item_id, item_translation)

        item_widget.show_all()

        self.items[item_id] = item_translation
        self.item_widgets[item_id] = item_widget

        self.item_list_box.insert(item_widget, position)

    def on_item_selected(
        self, listbox: Gtk.ListBox, row: Optional[TouchComboBoxItem]
    ) -> None:
        """React to an item being selected in the popover.

        Hide the popover and emit the ::changed signal.

        Args:
            listbox (Gtk.ListBox): Description
            row (Optional[TouchComboBoxItem]): Description
        """
        self.popover.popdown()

        if row is None:
            self.active_id = None
            self.active_label.set_text("")

        else:
            self.active_id = row.item_id
            self.active_label.set_text(self.items[self.active_id])

        self.emit("changed", self.active_id)

    def get_active_id(self) -> Optional[str]:
        """Return the ID of the currently selected item.

        Returns:
            Optional[str]: The currently selected item ID or None if no item is selected.
        """
        return self.active_id

    def set_active_id(self, item_id: Optional[str]):
        """Set the currently selected item by item ID.

        Args:
            item_id (Optional[str]): The ID of the item to select or None to unselect all items.

        Raises:
            KeyError: If the provided item ID does not exist.
        """
        if item_id in self.items:
            self.item_list_box.select_row(self.item_widgets[item_id])
        elif item_id is None:
            self.active_label.set_text("")
            self.item_list_box.unselect_all()
        else:
            raise KeyError(f'"{item_id}" is not an item of this TouchComboBox')

    def grab_focus(self):
        """Focus the TouchComboBox button."""
        self.menu_button.grab_focus()


GObject.type_ensure(TouchComboBox)
