"""A Gtk.Box that acts as a keyboard replacement."""

from typing import Union, Optional, Dict, Tuple

import time

from gi.repository import GObject, GLib, Gdk, Gtk  # type: ignore

from . import osk_util


# If shift is pressed twice in this time (seconds), activate caps lock
CAPS_DOUBLE_CLICK_TIME: float = 1

BKSP_REPEAT_DELAY: float = 0.4
BKSP_REPEAT_INTERVAL: float = 0.025


@Gtk.Template(resource_path="/de/linusmathieu/Liegensteuerung/keyboard.ui")
class OnscreenKeyboard(Gtk.Grid):
    """A Gtk.Box that acts as a keyboard replacement."""

    __gtype_name__ = "OnscreenKeyboard"

    button_a00: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a01: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a02: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a03: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a04: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a05: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a06: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a07: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a08: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a09: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_a10: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    button_b00: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b01: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b02: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b03: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b04: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b05: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b06: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b07: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b08: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b09: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_b10: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    button_c00: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c01: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c02: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c03: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c04: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c05: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c06: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c07: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c08: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c09: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_c10: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    button_d00: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d01: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d02: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d03: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d04: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d05: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_d06: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    button_e00: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_e01: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    button_e02: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    shift_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    alt_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()
    bksp_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    space_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    close_button: Union[Gtk.Button, Gtk.Template.Child] = Gtk.Template.Child()

    shift_active: bool = False
    shift_lock: bool = False

    alt_active: bool = False

    shift_activation_time: float = 0

    bksp_pressed: bool = False

    dest_window: Optional[Gtk.Window]

    def __init__(self, dest_window: Optional[Gtk.Window] = None, **kwargs):
        """Create a new OnscreenKeyboard.

        Args:
            dest_window (Optional[Gtk.Window]): The Gtk.Window to insert text
                into, or None (default) to take the parent window (toplevel)
            **kwargs: Arguments passed on to Gtk.Box
        """
        super().__init__(**kwargs)

        self.dest_window = dest_window

    def do_parent_set(self, old_parent: Optional[Gtk.Widget]) -> None:
        """React to the parent being set.

        When this method is called, it is assumed that all sub-widgets are
        ready to have signals connected.

        Args:
            old_parent (Optional[Gtk.Widget]): The old parent
        """
        if self.get_parent() is None:
            return

        # Order of defining tuple:
        # ((lowercase, label), (uppercase, label), (shiftlock, label), (alt + lowercase, label), (alt + uppercase, label), (alt + shiftlock, label))
        self.INSERT_KEYS: Dict[
            Gtk.Button, Tuple[Tuple[str, str], Tuple[str, str], Tuple[str, str]]
        ] = {
            self.button_a00: (
                ("1", "1"),
                ("!", "!"),
                ("1", "1"),
                ("¡", "¡"),
                ("", ""),
                ("", ""),
            ),
            self.button_a01: (
                ("2", "2"),
                ('"', '"'),
                ("2", "2"),
                ("'", "'"),
                ("", ""),
                ("", ""),
            ),
            self.button_a02: (
                ("3", "3"),
                ("§", "§"),
                ("3", "3"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_a03: (
                ("4", "4"),
                ("$", "$"),
                ("4", "4"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_a04: (
                ("5", "5"),
                ("%", "%"),
                ("5", "5"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_a05: (
                ("6", "6"),
                ("&", "&"),
                ("6", "6"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_a06: (
                ("7", "7"),
                ("/", "/"),
                ("7", "7"),
                ("\\", "\\"),
                ("", ""),
                ("", ""),
            ),
            self.button_a07: (
                ("8", "8"),
                ("(", "("),
                ("8", "8"),
                ("[", "["),
                ("{", "{"),
                ("{", "{"),
            ),
            self.button_a08: (
                ("9", "9"),
                (")", ")"),
                ("9", "9"),
                ("]", "]"),
                ("}", "}"),
                ("}", "}"),
            ),
            self.button_a09: (
                ("0", "0"),
                ("=", "="),
                ("0", "0"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_a10: (
                ("ß", "ß"),
                ("?", "?"),
                ("ẞ", "ẞ"),
                ("\\", "\\"),
                ("¿", "¿"),
                ("¿", "¿"),
            ),
            self.button_b00: (
                ("q", "q"),
                ("Q", "Q"),
                ("Q", "Q"),
                ("@", "@"),
                ("@", "@"),
                ("@", "@"),
            ),
            self.button_b01: (
                ("w", "w"),
                ("W", "W"),
                ("W", "W"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_b02: (
                ("e", "e"),
                ("E", "E"),
                ("E", "E"),
                ("€", "€"),
                ("€", "€"),
                ("€", "€"),
            ),
            self.button_b03: (
                ("r", "r"),
                ("R", "R"),
                ("R", "R"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_b04: (
                ("t", "t"),
                ("T", "T"),
                ("T", "T"),
                ("þ", "þ"),
                ("Þ", "Þ"),
                ("Þ", "Þ"),
            ),
            self.button_b05: (
                ("z", "z"),
                ("Z", "Z"),
                ("Z", "Z"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_b06: (
                ("u", "u"),
                ("U", "U"),
                ("U", "U"),
                ("ú", "ú"),
                ("Ú", "Ú"),
                ("Ú", "Ú"),
            ),
            self.button_b07: (
                ("i", "i"),
                ("I", "I"),
                ("I", "I"),
                ("í", "í"),
                ("Í", "Í"),
                ("Í", "Í"),
            ),
            self.button_b08: (
                ("o", "o"),
                ("O", "O"),
                ("O", "O"),
                ("ó", "ó"),
                ("Ó", "Ó"),
                ("Ó", "Ó"),
            ),
            self.button_b09: (
                ("p", "p"),
                ("P", "P"),
                ("P", "P"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_b10: (
                ("ü", "ü"),
                ("Ü", "Ü"),
                ("Ü", "Ü"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_c00: (
                ("a", "a"),
                ("A", "A"),
                ("A", "A"),
                ("á", "á"),
                ("Á", "Á"),
                ("Á", "Á"),
            ),
            self.button_c01: (
                ("s", "s"),
                ("S", "S"),
                ("S", "S"),
                ("ş", "ş"),
                ("Ş", "Ş"),
                ("Ş", "Ş"),
            ),
            self.button_c02: (
                ("d", "d"),
                ("D", "D"),
                ("D", "D"),
                ("ð", "ð"),
                ("Ð", "Ð"),
                ("Ð", "Ð"),
            ),
            self.button_c03: (
                ("f", "f"),
                ("F", "F"),
                ("F", "F"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_c04: (
                ("g", "g"),
                ("G", "G"),
                ("G", "G"),
                ("ŋ", "ŋ"),
                ("Ŋ", "Ŋ"),
                ("Ŋ", "Ŋ"),
            ),
            self.button_c05: (
                ("h", "h"),
                ("H", "H"),
                ("H", "H"),
                ("ħ", "ħ"),
                ("Ħ", "Ħ"),
                ("Ħ", "Ħ"),
            ),
            self.button_c06: (
                ("j", "j"),
                ("J", "J"),
                ("J", "J"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_c07: (
                ("k", "k"),
                ("K", "K"),
                ("K", "K"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_c08: (
                ("l", "l"),
                ("L", "L"),
                ("L", "L"),
                ("ł", "ł"),
                ("Ł", "Ł"),
                ("Ł", "Ł"),
            ),
            self.button_c09: (
                ("ö", "ö"),
                ("Ö", "Ö"),
                ("Ö", "Ö"),
                ("ø", "ø"),
                ("Ø", "Ø"),
                ("Ø", "Ø"),
            ),
            self.button_c10: (
                ("ä", "ä"),
                ("Ä", "Ä"),
                ("Ä", "Ä"),
                ("å", "å"),
                ("Å", "Å"),
                ("Å", "Å"),
            ),
            self.button_d00: (
                ("y", "y"),
                ("Y", "Y"),
                ("Y", "Y"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_d01: (
                ("x", "x"),
                ("X", "X"),
                ("X", "X"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_d02: (
                ("c", "c"),
                ("C", "C"),
                ("C", "C"),
                ("ç", "ç"),
                ("Ç", "Ç"),
                ("Ç", "Ç"),
            ),
            self.button_d03: (
                ("v", "v"),
                ("V", "V"),
                ("V", "V"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_d04: (
                ("b", "b"),
                ("B", "B"),
                ("B", "B"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_d05: (
                ("n", "n"),
                ("N", "N"),
                ("N", "N"),
                ("ñ", "ñ"),
                ("Ñ", "Ñ"),
                ("Ñ", "Ñ"),
            ),
            self.button_d06: (
                ("m", "m"),
                ("M", "M"),
                ("M", "M"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_e00: (
                (",", ","),
                (";", ";"),
                (",", ","),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_e01: (
                (".", "."),
                (":", ":"),
                (".", "."),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.button_e02: (
                ("-", "-"),
                ("_", "_"),
                ("-", "-"),
                ("", ""),
                ("", ""),
                ("", ""),
            ),
            self.space_button: (
                (" ", " "),
                (" ", " "),
                (" ", " "),
                (" ", " "),
                (" ", " "),
                (" ", " "),
            ),
        }

        self.KEYS: Dict[Gtk.Button, Tuple[str, str, str]] = {
            # Get all labels from self.INSERT_KEYS
            **{
                key: tuple([label for text, label in self.INSERT_KEYS[key]])
                for key in self.INSERT_KEYS
            },
            self.alt_button: 6 * ("⌥ Alt",),
            self.shift_button: 2 * ("⇧ Shift", "⇧ Shift", "⇪ Shift"),
            self.bksp_button: 6 * ("⌫",),
        }

        for key in self.INSERT_KEYS:
            key.connect("clicked", self.on_key_clicked)

        self.update_labels()

        self.shift_button.connect("clicked", self.on_shift_clicked)
        self.alt_button.connect("clicked", self.on_alt_clicked)
        self.bksp_button.connect("button-press-event", self.on_bksp_pressed)
        self.bksp_button.connect("button-release-event", self.on_bksp_released)

        self.close_button.connect("clicked", self.on_close_clicked)

    def on_key_clicked(self, button: Gtk.Button) -> None:
        """React to a button (key) being clicked.

        Only useful for keys that insert a string.

        Args:
            button (Gtk.Button): The clicked button
            lowercase (str): The string to insert if shift is not active
            uppercase (str): The string to insert if shift is active
        """
        insert_text: str

        if self.alt_active:
            if self.shift_lock:
                insert_text = self.INSERT_KEYS[button][5][0]
            elif self.shift_active:
                insert_text = self.INSERT_KEYS[button][4][0]
            else:
                insert_text = self.INSERT_KEYS[button][3][0]

        else:
            if self.shift_lock:
                insert_text = self.INSERT_KEYS[button][2][0]
            elif self.shift_active:
                insert_text = self.INSERT_KEYS[button][1][0]
            else:
                insert_text = self.INSERT_KEYS[button][0][0]

        focus_widget: Gtk.Widget
        if self.dest_window is not None:
            focus_widget = self.dest_window.get_focus()
        else:
            focus_widget = self.get_toplevel().get_focus()

        if isinstance(focus_widget, Gtk.Editable):
            focus_widget.insert_text(insert_text, focus_widget.get_position())
            focus_widget.set_position(focus_widget.get_position() + len(insert_text))

        if not self.shift_lock:
            self.shift_active = False
            self.shift_button.get_style_context().remove_class("active")

        self.update_labels()

    def on_shift_clicked(self, button: Gtk.Button) -> None:
        """React to a the shift button (key) being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        if not self.shift_active:
            button.get_style_context().add_class("active")
            self.shift_activation_time = time.time()
            self.shift_active = True

        elif self.shift_lock:
            button.get_style_context().remove_class("active")
            button.get_style_context().remove_class("locked")
            self.shift_active = False
            self.shift_lock = False

        elif self.shift_activation_time > time.time() - CAPS_DOUBLE_CLICK_TIME:
            button.get_style_context().add_class("active")
            button.get_style_context().add_class("locked")
            self.shift_lock = True

        else:
            button.get_style_context().remove_class("active")
            self.shift_active = False

        self.update_labels()

    def on_alt_clicked(self, button: Gtk.Button) -> None:
        """React to a the alt button (key) being clicked.

        Args:
            button (Gtk.Button): The clicked button
        """
        if not self.alt_active:
            button.get_style_context().add_class("active")
            self.alt_active = True

        else:
            button.get_style_context().remove_class("active")
            self.alt_active = False

        self.update_labels()

    def on_bksp_pressed(self, button: Gtk.Button, event: Gdk.EventButton) -> None:
        """Rect to the backspace button (key) being pressed.

        Args:
            button (Gtk.Button): The clicked button
            event (Gdk.EventButton): The Gdk.EventButton that triggered the
                signal
        """
        self.bksp_pressed = True

        focus_widget: Gtk.Widget
        if self.dest_window is not None:
            focus_widget = self.dest_window.get_focus()
        else:
            focus_widget = self.get_toplevel().get_focus()

        if isinstance(focus_widget, Gtk.Editable):
            focus_widget.delete_text(
                focus_widget.get_position() - 1, focus_widget.get_position()
            )

        GLib.timeout_add(int(BKSP_REPEAT_DELAY * 1000), self.on_bksp_hold)

    def on_bksp_hold(self):
        """React to thebackspace button being held for more than 0.3s."""

        if self.bksp_pressed:
            focus_widget: Gtk.Widget
            if self.dest_window is not None:
                focus_widget = self.dest_window.get_focus()
            else:
                focus_widget = self.get_toplevel().get_focus()

            if isinstance(focus_widget, Gtk.Editable):
                focus_widget.delete_text(
                    focus_widget.get_position() - 1, focus_widget.get_position()
                )

            GLib.timeout_add(int(BKSP_REPEAT_INTERVAL * 1000), self.on_bksp_hold)

    def on_bksp_released(self, button: Gtk.Button, event: Gdk.EventButton) -> None:
        """Rect to the backspace button (key) being released.

        Args:
            button (Gtk.Button): The clicked button
            event (Gdk.EventButton): The Gdk.EventButton that triggered the
                signal
        """
        self.bksp_pressed = False

    def on_close_clicked(self, button: Gtk.Button):
        """React to the user clicking the close button. Close the OSK.

        Args:
            button (Gtk.Button): The close button
        """
        osk_util.keyboard_show = True
        osk_util.unrequest_keyboard()

    def update_labels(self):
        """Update the key labels according to modifiers."""
        if self.alt_active:
            if self.shift_lock:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][5].strip())
                    key.set_sensitive(len(self.KEYS[key][5]) > 0)
            elif self.shift_active:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][4].strip())
                    key.set_sensitive(len(self.KEYS[key][4]) > 0)
            else:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][3].strip())
                    key.set_sensitive(len(self.KEYS[key][3]) > 0)

        else:
            if self.shift_lock:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][2].strip())
                    key.set_sensitive(len(self.KEYS[key][2]) > 0)
            elif self.shift_active:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][1].strip())
                    key.set_sensitive(len(self.KEYS[key][1]) > 0)
            else:
                for key in self.KEYS:
                    key.get_child().set_markup(self.KEYS[key][0].strip())
                    key.set_sensitive(len(self.KEYS[key][0]) > 0)


# Make OnscreenKeyboard accessible via .ui files
GObject.type_ensure(OnscreenKeyboard)
