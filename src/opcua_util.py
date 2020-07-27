"""
Abstraction layer on top of the opcua Python module.

Also specifies all used variable names.
"""

from typing import Dict, Any, Optional
from opcua import Client  # type: ignore
from opcua.common.node import Node  # type: ignore

prefix: str = "ns=4;s=|var|CODESYS Control for Raspberry Pi SL.Application."

program_prefix: str = "GVL_Tabelle.stTabelle_PrgDat."
setup_prefix: str = "Application.GVL_Visu_Einrichten."
main_prefix: str = "GVL_Visu_Haupt."

node_ids: Dict[str, Dict[str, str]] = {
    "program": {
        "id": prefix + program_prefix + "iProgramm_Nummer",
        #
        # Distances
        "pusher_left_distance_up": prefix
        + program_prefix
        + "iWeg_Pusher_A_Vor",
        "pusher_left_distance_down": prefix
        + program_prefix
        + "iWeg_Pusher_A_Rueck",
        "pusher_right_distance_up": prefix
        + program_prefix
        + "iWeg_Pusher_B_Vor",
        "pusher_right_distance_down": prefix
        + program_prefix
        + "iWeg_Pusher_B_Rueck",
        #
        # Pusher speeds (apparently I'll have to calculate push time myself,
        #                so it's commented out)
        #
        # "pusher_left_speed_up": prefix + program_prefix + "",
        # "pusher_left_speed_down": prefix + program_prefix + "",
        # "pusher_right_speed_up": prefix + program_prefix + "",
        # "pusher_right_speed_down": prefix + program_prefix + "",
        #
        # Push times (calculated from speed)
        "pusher_left_push_time_up": prefix
        + program_prefix
        + "iZeit_Pusher_A_Vor",
        "pusher_left_push_time_down": prefix
        + program_prefix
        + "iZeit_Pusher_A_Rueck",
        "pusher_right_push_time_up": prefix
        + program_prefix
        + "iZeit_Pusher_B_Vor",
        "pusher_right_push_time_down": prefix
        + program_prefix
        + "iZeit_Pusher_B_Rueck",
        #
        # Push delays
        "pusher_left_delay_up": prefix
        + program_prefix
        + "iDelay_Pusher_A_Vor",
        "pusher_left_delay_down": prefix
        + program_prefix
        + "iDelay_Pusher_A_Rueck",
        "pusher_right_delay_up": prefix
        + program_prefix
        + "iDelay_Pusher_B_Vor",
        "pusher_right_delay_down": prefix
        + program_prefix
        + "iDelay_Pusher_B_Rueck",
        #
        # Push wait times
        "pusher_left_stay_duration_up": prefix
        + program_prefix
        + "iWarten_Pusher_A_Vor",
        "pusher_left_stay_duration_down": prefix
        + program_prefix
        + "iWarten_Pusher_A_Rueck",
        "pusher_right_stay_duration_up": prefix
        + program_prefix
        + "iWarten_Pusher_B_Vor",
        "pusher_right_stay_duration_down": prefix
        + program_prefix
        + "iWarten_Pusher_B_Rueck",
        #
        # Push counts
        "pusher_left_push_count_up": prefix
        + program_prefix
        + "iWiederholung_Pusher_A_Vor",
        "pusher_left_push_count_down": prefix
        + program_prefix
        + "iWiederholung_Pusher_A_Rueck",
        "pusher_right_push_count_up": prefix
        + program_prefix
        + "iWiederholung_Pusher_B_Vor",
        "pusher_right_push_count_down": prefix
        + program_prefix
        + "iWiederholung_Pusher_B_Rueck",
        #
        # Distance correction per 7deg
        "pusher_left_distance_correction_up": prefix
        + program_prefix
        + "iWinkelkorrektur_Pusher_A_Vor",
        "pusher_left_distance_correction_down": prefix
        + program_prefix
        + "iWinkelkorrektur_Pusher_A_Rueck",
        "pusher_right_distance_correction_up": prefix
        + program_prefix
        + "iWinkelkorrektur_Pusher_B_Vor",
        "pusher_right_distance_correction_down": prefix
        + program_prefix
        + "iWinkelkorrektur_Pusher_B_Rueck",
        #
        # Angle changes in deg (per push I guess)
        "angle_change_up": prefix + program_prefix + "iWinkelaenderung_Vor",
        "angle_change_down": prefix
        + program_prefix
        + "iWinkelaenderung_Rueck",
        "push_distance_up": prefix + program_prefix + "iVorschub_Vor",
        "push_distance_down": prefix + program_prefix + "iVorschub_Rueck",
        #
        # Push counts (idk if these are calculated, but they're in the OPCUA
        #              vars, so I'm including them here)
        "push_count_up": prefix + program_prefix + "iAnzahl_Vorschuebe_Vor",
        "push_count_down": prefix
        + program_prefix
        + "iAnzahl_Vorschuebe_Rueck",
        "pass_count_up": prefix + program_prefix + "iWiederholungen_Vor",
        "pass_count_down": prefix + program_prefix + "iWiederholungen_Rueck",
        "pass_count_total": prefix + program_prefix + "iWiederholungen_Gesamt",
    },
    "setup": {
        # Displayed values
        "tilt": prefix + setup_prefix + "iAnzeige_Kippwinkel",
        "left_pusher": prefix + setup_prefix + "iAnzeige_Position_Pusher_A",
        "right_pusher": prefix + setup_prefix + "iAnzeige_Position_Pusher_B",
        "left_right": prefix + setup_prefix + "iAnzeige_Position_links_rechts",
        "up_down": prefix + setup_prefix + "iAnzeige_Position_vor_rueck",
        # Mysterious button that has an int for some reason
        "fast_up_button": prefix + setup_prefix + "iBut_FF_Puscher_hoch",
        "fast_down_button": prefix + setup_prefix + "iBut_FF_Puscher_runter",
        # Reset button
        "reset_axes_button": prefix + setup_prefix + "xBut_Grundstellung",
        # Tilt buttons
        "tilt_down_button": prefix + setup_prefix + "xBut_Kipp_kaudal",
        "tilt_up_button": prefix + setup_prefix + "xBut_Kipp_kranial",
        # Pusher buttons
        "left_move_in_button": prefix
        + setup_prefix
        + "xBut_pusher_A_hoch_5mm",
        "left_move_out_button": prefix
        + setup_prefix
        + "xBut_pusher_A_runter_5mm",
        "right_move_in_button": prefix
        + setup_prefix
        + "xBut_pusher_B_hoch_5mm",
        "righ_movet_out_button": prefix
        + setup_prefix
        + "xBut_pusher_B_runter_5mm",
        # Movement buttons
        "move_left_button": prefix + setup_prefix + "xBut_links",
        "move_right_button": prefix + setup_prefix + "xBut_rechts",
        "move_up_button": prefix + setup_prefix + "xBut_rueck_5mm",
        "move_down_button": prefix + setup_prefix + "xBut_vor_5mm",
    },
    "main": {
        #
        # Displayed values
        "passes": prefix + main_prefix + "iAnzeige_Gesamt_Durchlauf",
        "tilt": prefix + main_prefix + "iAnzeige_Kippwinkel",
        "left_pusher": prefix + main_prefix + "iAnzeige_Position_Pusher_A",
        "right_pusher": prefix + main_prefix + "iAnzeige_Position_Pusher_B",
        "left_right": prefix + main_prefix + "iAnzeige_Position_links_rechts",
        "up_down": prefix + main_prefix + "iAnzeige_Position_vor_rueck",
        "is_pusher_active": prefix + main_prefix + "xAlarm_Pfeil",
        #
        # Buttons
        "emergency_off_button": prefix + main_prefix + "xBut_NOTAUS",
        # Do I need this?
        "power_button": prefix + main_prefix + "xBut_Power",
        "reset_button": prefix + main_prefix + "xBut_Reset",
        "start_button": prefix + main_prefix + "xBut_Start",
        #
        # "Visibility" of different "pop-ups"
        "emergency_off": prefix + main_prefix + "xSichtbarkeit_NOTAUS_PopUp",
        "not_referenced": prefix
        + main_prefix
        + "xSichtbarkeit_NichtRef_PopUp",
        "referencing": prefix
        + main_prefix
        + "xSichtbarkeit_Referenzierung_PopUp",
    },
}


class Singleton(type):
    """A singleton metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NodeCategory:
    """A category of Node objects (by name)."""

    def __init__(self, node_dict: Dict[str, Node]):
        """Create a new NodeCategory.

        Args:
            node_dict (Dict[str, Node]): A dict of node names and the
                corresponding Node objects to represent as a category
        """
        self.nodes = node_dict

    def __getitem__(self, name: str) -> Any:
        """Get the value of a Node in this category.

        Args:
            name (str): The name of the node

        Returns:
            Any: The value of the node

        Raises:
            AttributeError: If the node does not exist
        """
        if name == "nodes":
            return self.__dict__["nodes"]

        if name not in self.nodes:
            raise AttributeError(f"{name} is not a node of this NodeCategory")

        try:
            return self.nodes[name].get_value()
        except BrokenPipeError:
            Connection().connect()

            return self.nodes[name].get_value()

    def __setitem__(self, name: str, value: Any) -> None:
        """Set the value of a Node in this category.

        Args:
            name (str): The name of the node
            value (Any): The new value of the node

        Raises:
            AttributeError: If the node does not exist
        """
        if name not in self.nodes:
            raise AttributeError(f"{name} is not a node of this NodeCategory")

        try:
            self.nodes[name].set_value(
                value, self.nodes[name].get_data_type_as_variant_type()
            )
        except BrokenPipeError:
            Connection().connect()

            self.nodes[name].set_value(
                value, self.nodes[name].get_data_type_as_variant_type()
            )


class Connection(metaclass=Singleton):
    """A connection to the Liegensteuerung OPC UA server."""

    client: Client
    connection: Optional["Connection"] = None

    def __init__(self):
        """Create a new Connection."""
        self.client = Client("opc.tcp://localhost:4840")
        self.connect()

        self.node_categories: Dict[str, NodeCategory] = dict()

        for node_category in node_ids:
            category_dict: [str, Node] = dict()
            for node_name in node_ids[node_category]:
                category_dict[node_name] = self.client.get_node(
                    node_ids[node_category][node_name]
                )

            self.node_categories[node_category] = NodeCategory(category_dict)

    def connect(self):
        """Connect to the OPC UA server."""
        self.client.connect()

    def __getitem__(self, name: str) -> NodeCategory:
        """Get a NodeCategory if it exists.

        Args:
            name (str): The name of the node category

        Returns:
            NodeCategory: A matching NodeCategory

        Raises:
            AttributeError: If the node category does not exist
        """
        if name not in self.node_categories:
            raise AttributeError(f"{name} is not a node categroy")

        return self.node_categories[name]
