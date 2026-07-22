"""
Utility functions for SimWorld social interaction demos.

Extracted from:
  - social_interaction_demo.ipynb
  - sidewalk_agent_placement.ipynb
"""

import math
import random
from typing import Optional

from simworld.agent.humanoid import Humanoid
from simworld.utils.vector import Vector

# ---------------------------------------------------------------------------
# Blueprint path constants
# ---------------------------------------------------------------------------

# MetaHuman action-specific rigs (recommended for social interaction clips)
BP_METAHUMAN      = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_MetaHuman.BP_MetaHuman_C'
BP_DISCUSSION1    = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Discussion1.BP_Discussion1_C'
BP_DISCUSSION2    = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Discussion2.BP_Discussion2_C'
BP_ARGUMENT1      = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Argument1.BP_Argument1_C'
BP_ARGUMENT2      = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Argument2.BP_Argument2_C'
BP_LISTENER       = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Listener.BP_Listener_C'
BP_DIRECTOR       = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Director.BP_Director_C'
BP_DRIVER         = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_Driver.BP_Driver_C'
BP_SIT_STAND      = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_SitDownAndStander.BP_SitDownAndStander_C'
BP_PICKUP_HEAVY_0 = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_PickUpHeavy_0.BP_PickUpHeavy_0_C'
BP_PICKUP_HEAVY_1 = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_PickUpHeavy_1.BP_PickUpHeavy_1_C'
BP_ENTER_VEHICLE  = '/Game/Human_Avatar/MetaHumanCharacter/Blueprint/BP_EnterVihicle.BP_EnterVihicle_C'

# TrafficSystem agents
BP_USER_AGENT       = '/Game/TrafficSystem/Pedestrian/Base_User_Agent.Base_User_Agent_C'
BP_PEDESTRIAN       = '/Game/TrafficSystem/Pedestrian/Base_Pedestrian.Base_Pedestrian_C'
BP_PEDESTRIAN_SPEED = '/Game/TrafficSystem/Pedestrian/Base_Pedestrian_WithSpeed.Base_Pedestrian_WithSpeed_C'
BP_DELIVERY_MAN     = '/Game/TrafficSystem/Pedestrian/BP_DeliveryMan.BP_DeliveryMan_C'

# Default Mannequin avatar
BP_DEFAULT_CHARACTER = '/Game/Human_Avatar/DefaultCharacter/Blueprint/BP_Default_Character.BP_Default_Character_C'


# ---------------------------------------------------------------------------
# Agent spawning
# ---------------------------------------------------------------------------

def spawn_humanoid(communicator, config, position: Vector, direction: Vector,
                   name: str, blueprint_path: str) -> Humanoid:
    """Spawn a humanoid at position facing direction. Returns the Humanoid object."""
    agent = Humanoid(
        position=position,
        direction=direction,
        communicator=communicator,
        config=config,
    )
    communicator.spawn_agent(
        agent,
        name=name,
        model_path=blueprint_path,
        type='humanoid',
        position=(position.x, position.y, 100),
    )
    return agent


# ---------------------------------------------------------------------------
# Agent orientation
# ---------------------------------------------------------------------------

def set_agent_orientation(
        communicator,
        agent_name: str,
        from_pos: Optional[Vector] = None,
        to_pos: Optional[Vector] = None,
        yaw_deg: Optional[float] = None,
        yaw_offset_deg: float = 0.0,
        pitch_deg: float = 0.0):
    """Set agent orientation with precise angle control.

    Modes (mutually exclusive for the base angle):
    - Face-toward mode: provide from_pos + to_pos.
      Computes the yaw that makes the agent look from from_pos toward to_pos.
    - Absolute mode: provide yaw_deg directly.
      UE yaw convention: 0deg = +X axis, 90deg = +Y, 180deg = -X, -90deg = -Y.

    Args:
        communicator:    SimWorld Communicator instance.
        agent_name:      UE actor name of the humanoid.
        from_pos:        Agent's current position (Vector). Used in face-toward mode.
        to_pos:          Target position to face (Vector). Used in face-toward mode.
        yaw_deg:         Explicit yaw angle in degrees. Used in absolute mode.
        yaw_offset_deg:  Additive offset applied after the base angle.
                         Positive values rotate clockwise (to the right).
                         Useful for slight off-axis glances or artistic offsets.
        pitch_deg:       Vertical tilt. Normally 0 for standing agents.
                         Positive = look down, negative = look up (UE convention).
    """
    if yaw_deg is not None:
        base_yaw = yaw_deg
    elif from_pos is not None and to_pos is not None:
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        base_yaw = math.degrees(math.atan2(dy, dx))
    else:
        raise ValueError("Provide either yaw_deg or both from_pos and to_pos.")

    communicator.unrealcv.set_orientation([pitch_deg, base_yaw + yaw_offset_deg, 0], agent_name)


# ---------------------------------------------------------------------------
# Social interaction actions
# ---------------------------------------------------------------------------

def trigger_action(ucv, agent_name: str, role: str,
                   interaction_type: str = 'discuss', variant: int = 0):
    """Trigger a social animation on agent_name based on its role.

    Args:
        ucv:              UnrealCV instance.
        agent_name:       UE actor name of the humanoid.
        role:             'speak', 'listen', or 'wave'.
        interaction_type: 'discuss', 'argue', or 'direct'. Only used when role='speak'.
        variant:          Animation variant index (0 or 1). Only used for discuss/argue.
    """
    if role == 'speak':
        if interaction_type == 'discuss':
            ucv.humanoid_discuss(agent_name, discuss_type=variant)
        elif interaction_type == 'argue':
            ucv.humanoid_argue(agent_name, argue_type=variant)
        elif interaction_type == 'direct':
            ucv.humanoid_directing_path(agent_name)
    elif role == 'listen':
        ucv.humanoid_listen(agent_name)
    elif role == 'wave':
        ucv.humanoid_wave_to_dog(agent_name)


def dispatch_social_action(ucv, agent_name: str, action_str: str):
    """Translate an action string (as returned by an LLM) into a ucv call.

    Supported action strings:
      'listen'      -> humanoid_listen
      'direct'      -> humanoid_directing_path
      'wave'        -> humanoid_wave_to_dog
      'discuss:N'   -> humanoid_discuss(variant=N)
      'argue:N'     -> humanoid_argue(variant=N)

    Args:
        ucv:         UnrealCV instance.
        agent_name:  UE actor name of the humanoid.
        action_str:  Action string produced by the LLM.
    """
    if action_str == 'listen':
        ucv.humanoid_listen(agent_name)
    elif action_str == 'direct':
        ucv.humanoid_directing_path(agent_name)
    elif action_str == 'wave':
        ucv.humanoid_wave_to_dog(agent_name)
    elif action_str and action_str.startswith('discuss:'):
        variant = int(action_str.split(':')[1])
        ucv.humanoid_discuss(agent_name, variant)
    elif action_str and action_str.startswith('argue:'):
        variant = int(action_str.split(':')[1])
        ucv.humanoid_argue(agent_name, variant)
    else:
        print(f"[warn] unknown action {action_str!r}, skipping")


# ---------------------------------------------------------------------------
# Sidewalk sampling
# ---------------------------------------------------------------------------

def sample_sidewalk_positions(
        city_map,
        agent_spacing_cm: float = 100.0,
        min_edge_length_cm: float = 3000.0,
        edge_index: Optional[int] = None,
        seed: Optional[int] = None,
) -> tuple:
    """Pick two agent positions symmetrically placed along a sidewalk edge.

    The Map must already be initialised (city_map.initialize_map_from_file called).
    Sidewalk edges are offset ~1700 cm perpendicular from road centerlines.

    Args:
        city_map:           A simworld.map.map.Map instance.
        agent_spacing_cm:   Distance between the two agents along the edge (cm).
        min_edge_length_cm: Minimum edge length to consider; filters out short edges.
        edge_index:         Index into the filtered edge list to force a specific edge.
                            None = random selection.
        seed:               Random seed for reproducible selection. None = no seed.

    Returns:
        (pos_a, pos_b, chosen_edge) where pos_a and pos_b are Vector instances and
        chosen_edge is the selected Map edge.

    Raises:
        RuntimeError: If no sidewalk edges meet the minimum length requirement.
    """
    sidewalk_edges = [e for e in city_map.edges if e.type == 'sidewalk']
    long_edges = [
        e for e in sidewalk_edges
        if e.node1.position.distance(e.node2.position) >= min_edge_length_cm
    ]

    if not long_edges:
        raise RuntimeError(
            f"No sidewalk edges >= {min_edge_length_cm} cm found. "
            "Lower min_edge_length_cm or check that the map is loaded."
        )

    if edge_index is not None:
        chosen_edge = long_edges[edge_index]
    else:
        rng = random.Random(seed)
        chosen_edge = rng.choice(long_edges)

    p1 = chosen_edge.node1.position
    p2 = chosen_edge.node2.position

    edge_dir = (p2 - p1).normalize()
    mid = Vector((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    half = agent_spacing_cm / 2

    pos_a = Vector(mid.x - edge_dir.x * half, mid.y - edge_dir.y * half)
    pos_b = Vector(mid.x + edge_dir.x * half, mid.y + edge_dir.y * half)

    return pos_a, pos_b, chosen_edge
