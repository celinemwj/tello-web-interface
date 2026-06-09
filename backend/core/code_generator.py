from typing import Dict, Any, List
from djitellopy import Tello


NO_ARG_TEMPLATES = {
    "takeoff": "tello.takeoff()",
    "land": "tello.land()",
    "emergency": "tello.emergency()",
    "keepalive": "tello.send_keepalive()",

    "streamon": "tello.streamon()",
    "streamoff": "tello.streamoff()",

    "flip_forward": "tello.flip_forward()",
    "flip_back": "tello.flip_back()",
    "flip_left": "tello.flip_left()",
    "flip_right": "tello.flip_right()",

    "query_battery": "battery = tello.get_battery()",
    "query_speed": "speed = tello.get_speed()",
    "query_height": "height = tello.get_height()",
    "query_temperature": "temperature = tello.get_temperature()",
    "query_flight_time": "flight_time = tello.get_flight_time()",
    "query_attitude": "attitude = tello.get_current_state()",
    "query_barometer": "barometer = tello.get_barometer()",
    "query_acceleration": "state = tello.get_current_state()",
    "query_distance_tof": "tof = tello.get_distance_tof()",
    "query_wifi_snr": "wifi_snr = tello.query_wifi_signal_noise_ratio()",
}


VALUE_TEMPLATES = {
    "move_forward": "tello.move_forward({value})",
    "move_back": "tello.move_back({value})",
    "move_left": "tello.move_left({value})",
    "move_right": "tello.move_right({value})",
    "move_up": "tello.move_up({value})",
    "move_down": "tello.move_down({value})",

    "rotate_clockwise": "tello.rotate_clockwise({value})",
    "rotate_counter_clockwise": "tello.rotate_counter_clockwise({value})",

    "set_speed": "tello.set_speed({value})",
}


def generate_command_line(command: Dict[str, Any]) -> str:

    action = command["action"]

    if action in NO_ARG_TEMPLATES:
        return NO_ARG_TEMPLATES[action]

    if action in VALUE_TEMPLATES:
        value = command["value"]
        return VALUE_TEMPLATES[action].format(value=value)

    if action == "go_xyz_speed":
        return (
            f"tello.go_xyz_speed("
            f"{command['x']}, {command['y']}, {command['z']}, {command['speed']}"
            f")"
        )

    if action == "curve_xyz_speed":
        return (
            f"tello.curve_xyz_speed("
            f"{command['x1']}, {command['y1']}, {command['z1']}, "
            f"{command['x2']}, {command['y2']}, {command['z2']}, "
            f"{command['speed']}"
            f")"
        )

    raise ValueError(f"Unsupported action for code generation: {action}")


def generate_python_code(commands: List[Dict[str, Any]]) -> str:

    code_lines = [
        "from djitellopy import Tello",
        "",
        "tello = Tello()",
        "tello.connect()",
        "",
    ]

    for command in commands:
        code_lines.append(generate_command_line(command))

    code_lines.extend([
        "",
        "tello.end()",
    ])

    return "\n".join(code_lines)


def generate_code_from_llm_output(llm_output: Dict[str, Any]) -> str:

    commands = llm_output.get("commands", [])

    if not commands:
        raise ValueError("No commands found in LLM output.")

    return generate_python_code(commands)

def execute_command_with_tello(tello, command: Dict[str, Any]) -> Any:
    """
    Execute one validated command directly on a DJITelloPy Tello instance.

    This function does not execute generated code as a string.
    It calls the corresponding DJITelloPy method directly.
    """
    action = command["action"]

    if action == "takeoff":
        return tello.takeoff()

    if action == "land":
        return tello.land()

    if action == "emergency":
        return tello.emergency()

    if action == "keepalive":
        return tello.send_keepalive()

    if action == "streamon":
        return tello.streamon()

    if action == "streamoff":
        return tello.streamoff()

    if action == "flip_forward":
        return tello.flip_forward()

    if action == "flip_back":
        return tello.flip_back()

    if action == "flip_left":
        return tello.flip_left()

    if action == "flip_right":
        return tello.flip_right()

    if action == "move_forward":
        return tello.move_forward(command["value"])

    if action == "move_back":
        return tello.move_back(command["value"])

    if action == "move_left":
        return tello.move_left(command["value"])

    if action == "move_right":
        return tello.move_right(command["value"])

    if action == "move_up":
        return tello.move_up(command["value"])

    if action == "move_down":
        return tello.move_down(command["value"])

    if action == "rotate_clockwise":
        return tello.rotate_clockwise(command["value"])

    if action == "rotate_counter_clockwise":
        return tello.rotate_counter_clockwise(command["value"])

    if action == "set_speed":
        return tello.set_speed(command["value"])

    if action == "go_xyz_speed":
        return tello.go_xyz_speed(
            command["x"],
            command["y"],
            command["z"],
            command["speed"],
        )

    if action == "curve_xyz_speed":
        return tello.curve_xyz_speed(
            command["x1"],
            command["y1"],
            command["z1"],
            command["x2"],
            command["y2"],
            command["z2"],
            command["speed"],
        )

    if action == "query_battery":
        return tello.get_battery()

    if action == "query_speed":
        return tello.get_speed()

    if action == "query_height":
        return tello.get_height()

    if action == "query_temperature":
        return tello.get_temperature()

    if action == "query_flight_time":
        return tello.get_flight_time()

    if action == "query_attitude":
        return tello.get_current_state()

    if action == "query_barometer":
        return tello.get_barometer()

    if action == "query_acceleration":
        return tello.get_current_state()

    if action == "query_distance_tof":
        return tello.get_distance_tof()

    if action == "query_wifi_snr":
        return tello.query_wifi_signal_noise_ratio()

    raise ValueError(f"Unsupported action for Tello execution: {action}")


def execute_commands_with_tello(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute validated commands directly on a real DJI Tello using DJITelloPy.

    Important:
    - commands must already be validated before calling this function.
    - this function should only be used when the PC is connected to the Tello Wi-Fi.
    """
   

    tello = Tello()
    execution_results = []
    logs = []

    try:
        tello.connect()
        logs.append("connect: ok")

        battery = tello.get_battery()
        logs.append(f"battery: {battery}%")

        if battery < 20:
            return {
                "success": False,
                "execution_results": execution_results,
                "logs": logs,
                "error": "Battery too low for safe execution.",
                "final_state": None,
            }

        for command in commands:
            action = command["action"]
            response = execute_command_with_tello(tello, command)

            execution_results.append({
                "action": action,
                "response": response,
            })

            logs.append(f"{action}: {response}")

        final_state = tello.get_current_state()
        logs.append(f"final_state: {final_state}")

        tello.end()
        logs.append("end: ok")

        return {
            "success": True,
            "execution_results": execution_results,
            "logs": logs,
            "final_state": final_state,
        }

    except Exception as error:
        try:
            tello.end()
            logs.append("end: ok after error")
        except Exception:
            pass

        return {
            "success": False,
            "execution_results": execution_results,
            "logs": logs,
            "error": str(error),
            "final_state": None,
        }