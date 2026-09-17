from typing import Dict, Any, List, Tuple

ALLOWED_COMMANDS: Dict[str, Dict[str, Any]] = {

    "takeoff": {"requires_value": False},
    "land": {"requires_value": False},
    "emergency": {"requires_value": False},
    "keepalive": {"requires_value": False}, 

    "move_forward": {"requires_value": True, "min": 20, "max": 500},
    "move_back": {"requires_value": True, "min": 20, "max": 500},
    "move_left": {"requires_value": True, "min": 20, "max": 500},
    "move_right": {"requires_value": True, "min": 20, "max": 500},
    "move_up": {"requires_value": True, "min": 20, "max": 500},
    "move_down": {"requires_value": True, "min": 20, "max": 500},

    "go_xyz_speed": {
        "requires_xyz": True,
        "min": 20,
        "max": 500,
        "speed_min": 10,
        "speed_max": 100,
    },

    "curve_xyz_speed": {
        "requires_curve": True,
        "min": 20,
        "max": 500,
        "speed_min": 10,
        "speed_max": 60,
    },

    "rotate_clockwise": {"requires_value": True, "min": 1, "max": 3600},
    "rotate_counter_clockwise": {"requires_value": True, "min": 1, "max": 3600},

    "flip_forward": {"requires_value": False},
    "flip_back": {"requires_value": False},
    "flip_left": {"requires_value": False},
    "flip_right": {"requires_value": False},

    "set_speed": {"requires_value": True, "min": 10, "max": 100},

    "streamon": {"requires_value": False},
    "streamoff": {"requires_value": False},

    "query_battery": {"requires_value": False},
    "query_speed": {"requires_value": False},
    "query_attitude": {"requires_value": False},
    "query_height": {"requires_value": False},
    "query_temperature": {"requires_value": False},
    "query_flight_time": {"requires_value": False},
    "query_distance_tof": {"requires_value": False},
    "query_barometer": {"requires_value": False},
    "query_acceleration": {"requires_value": False},
    "query_wifi_snr": {"requires_value": False},
}

REQUIRES_AIRBORNE = {
    "move_forward",
    "move_back",
    "move_left",
    "move_right",
    "move_up",
    "move_down",
    "go_xyz_speed",
    "curve_xyz_speed",
    "rotate_clockwise",
    "rotate_counter_clockwise",
    "flip_forward",
    "flip_back",
    "flip_left",
    "flip_right",
    "land",
    "keepalive",
}

MAKES_AIRBORNE = {"takeoff"}
MAKES_GROUNDED = {"land", "emergency"}

def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def validate_axis_value(
    label: str,
    coord: str,
    value: Any,
    minimum: int,
    maximum: int,
    errors: List[str],
) -> None:

    if not is_number(value):
        errors.append(f"{label}: '{coord}' must be a number.")
        return

    if value == 0:
        return

    if not (minimum <= abs(value) <= maximum):
        errors.append(
            f"{label}: '{coord}' must be 0 or have an absolute value "
            f"between {minimum} and {maximum} cm."
        )


def validate_standard_value(
    label: str,
    cmd: Dict[str, Any],
    spec: Dict[str, Any],
    errors: List[str],
) -> None:
    if "value" not in cmd:
        errors.append(f"{label}: missing required 'value' field.")
        return

    value = cmd["value"]

    if not is_number(value):
        errors.append(f"{label}: 'value' must be a number, got {type(value).__name__}.")
        return

    if not (spec["min"] <= value <= spec["max"]):
        errors.append(
            f"{label}: value {value} out of range [{spec['min']}–{spec['max']}]."
        )

def validate_go_xyz_speed(
    label: str,
    cmd: Dict[str, Any],
    spec: Dict[str, Any],
    errors: List[str],
) -> None:
    for coord in ("x", "y", "z"):
        if coord not in cmd:
            errors.append(f"{label}: missing required field '{coord}'.")
        else:
            validate_axis_value(label, coord, cmd[coord], spec["min"], spec["max"], errors)

    if "speed" not in cmd:
        errors.append(f"{label}: missing required 'speed' field.")
    else:
        speed = cmd["speed"]
        if not is_number(speed):
            errors.append(f"{label}: 'speed' must be a number.")
        elif not (spec["speed_min"] <= speed <= spec["speed_max"]):
            errors.append(
                f"{label}: speed {speed} out of range "
                f"[{spec['speed_min']}–{spec['speed_max']}]."
            )

    if all(cmd.get(axis) == 0 for axis in ("x", "y", "z")):
        errors.append(f"{label}: x, y and z cannot all be 0.")

def validate_curve_xyz_speed(
    label: str,
    cmd: Dict[str, Any],
    spec: Dict[str, Any],
    errors: List[str],
) -> None:
    coordinates = ("x1", "y1", "z1", "x2", "y2", "z2")

    for coord in coordinates:
        if coord not in cmd:
            errors.append(f"{label}: missing required field '{coord}'.")
        else:
            validate_axis_value(label, coord, cmd[coord], spec["min"], spec["max"], errors)

    if "speed" not in cmd:
        errors.append(f"{label}: missing required 'speed' field.")
    else:
        speed = cmd["speed"]
        if not is_number(speed):
            errors.append(f"{label}: 'speed' must be a number.")
        elif not (spec["speed_min"] <= speed <= spec["speed_max"]):
            errors.append(
                f"{label}: curve speed {speed} out of range "
                f"[{spec['speed_min']}–{spec['speed_max']}]."
            )

    if all(cmd.get(coord) == 0 for coord in coordinates):
        errors.append(f"{label}: all curve coordinates cannot be 0.")

def validate_sequence(commands: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []

    airborne = False
    has_landed = False

    for i, cmd in enumerate(commands):
        if not isinstance(cmd, dict):
            continue

        action = cmd.get("action", "")

        if action not in ALLOWED_COMMANDS:
            continue

        # Once land has been executed, the mission is considered finished.
        # We reject any command after land in the same sequence.
        if has_landed and action not in {"emergency"}:
            errors.append(
                f"Command[{i}] ('{action}'): cannot execute commands after landing "
                f"in the same sequence."
            )
            continue

        # Commands that require flight cannot be executed before takeoff.
        if action in REQUIRES_AIRBORNE and not airborne:
            errors.append(
                f"Command[{i}] ('{action}'): drone is not airborne yet. "
                f"A 'takeoff' must come first."
            )
            continue

        # Cannot take off twice while already flying.
        if action == "takeoff":
            if airborne:
                errors.append(f"Command[{i}] ('takeoff'): drone is already airborne.")
                continue

        # Update drone state.
        if action in MAKES_AIRBORNE:
            airborne = True

        elif action in MAKES_GROUNDED:
            airborne = False
            has_landed = True

    return errors

def validate(llm_output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(llm_output, dict):
        return False, ["LLM output is not a dict."]

    status = llm_output.get("status")

    if status not in {"accepted", "rejected"}:
        errors.append("'status' must be either 'accepted' or 'rejected'.")

    if "commands" not in llm_output:
        errors.append("Missing field: 'commands'.")
        return False, errors

    if not isinstance(llm_output["commands"], list):
        errors.append("'commands' must be a list.")
        return False, errors

    if status == "rejected":
        reason = (
            llm_output.get("rejection_reason")
            or llm_output.get("explanation")
            or "LLM rejected the command."
        )
        return False, [reason]

    commands: List[Dict[str, Any]] = llm_output["commands"]

    if status == "accepted" and len(commands) == 0:
        errors.append("Accepted status but commands list is empty.")
        return False, errors

    for i, cmd in enumerate(commands):
        if not isinstance(cmd, dict):
            errors.append(f"Command[{i}]: must be a dict.")
            continue

        label = f"Command[{i}] ({cmd.get('action', '?')})"

        if "action" not in cmd:
            errors.append(f"Command[{i}]: missing 'action' field.")
            continue

        action = cmd["action"]

        if action not in ALLOWED_COMMANDS:
            errors.append(
                f"{label}: unknown action '{action}'. Not in allowed command list."
            )
            continue

        spec = ALLOWED_COMMANDS[action]

        if spec.get("requires_value"):
            validate_standard_value(label, cmd, spec, errors)

        elif spec.get("requires_xyz"):
            validate_go_xyz_speed(label, cmd, spec, errors)

        elif spec.get("requires_curve"):
            validate_curve_xyz_speed(label, cmd, spec, errors)


    errors.extend(validate_sequence(commands))

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_and_report(llm_output: Dict[str, Any]) -> Dict[str, Any]:
    is_valid, errors = validate(llm_output)

    return {
        "valid": is_valid,
        "errors": errors,
        "commands": llm_output.get("commands", []) if is_valid else [],
    }
