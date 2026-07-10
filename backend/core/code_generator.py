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

    "query_battery": "battery = tello.query_battery()",
    "battery?": "battery = tello.query_battery()",

    "query_speed": "speed = tello.query_speed()",
    "speed?": "speed = tello.query_speed()",

    "query_height": "height = tello.query_height()",
    "height?": "height = tello.query_height()",

    "query_temperature": "temperature = tello.query_temperature()",
    "temperature?": "temperature = tello.query_temperature()",

    "query_flight_time": "flight_time = tello.query_flight_time()",
    "time?": "flight_time = tello.query_flight_time()",

    "query_attitude": "attitude = tello.query_attitude()",

    "query_barometer": "barometer = tello.query_barometer()",
    "barometer?": "barometer = tello.query_barometer()",

    "query_acceleration": "state = tello.get_current_state()",

    "query_distance_tof": "tof = tello.query_distance_tof()",
    "tof?": "tof = tello.query_distance_tof()",

    "query_wifi_snr": "wifi_snr = tello.query_wifi_signal_noise_ratio()",
    "wifi?": "wifi_snr = tello.query_wifi_signal_noise_ratio()",
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


def safe_query(tello: Tello, query_function_name: str, default=None):
    try:
        query_function = getattr(tello, query_function_name)
        return query_function()
    except Exception:
        return default


def safe_read_tello_state(tello: Tello, streaming: bool = False) -> Dict[str, Any]:
    final_state = {
        "x": 0,
        "y": 0,
        "z": 0,
        "height": None,
        "yaw": None,
        "battery": None,
        "speed": None,
        "temperature": None,
        "tof": None,
        "wifi_snr": None,
        "flight_time": None,
        "barometer": None,
        "is_flying": False,
        "streaming": streaming,
    }

    final_state["battery"] = safe_query(tello, "query_battery")
    final_state["height"] = safe_query(tello, "query_height")
    final_state["speed"] = safe_query(tello, "query_speed")
    final_state["temperature"] = safe_query(tello, "query_temperature")
    final_state["tof"] = safe_query(tello, "query_distance_tof")
    final_state["wifi_snr"] = safe_query(tello, "query_wifi_signal_noise_ratio")
    final_state["flight_time"] = safe_query(tello, "query_flight_time")
    final_state["barometer"] = safe_query(tello, "query_barometer")

    try:
        raw_state = tello.get_current_state()

        if isinstance(raw_state, dict):
            final_state["yaw"] = raw_state.get("yaw", final_state["yaw"])
            final_state["speed"] = raw_state.get("vgx", final_state["speed"])
            final_state["height"] = raw_state.get("h", final_state["height"])
            final_state["battery"] = raw_state.get("bat", final_state["battery"])
            final_state["tof"] = raw_state.get("tof", final_state["tof"])
            final_state["flight_time"] = raw_state.get("time", final_state["flight_time"])

            if raw_state.get("temph") is not None:
                final_state["temperature"] = raw_state.get("temph")

    except Exception:
        pass

    return final_state


def execute_command_with_tello(tello: Tello, command: Dict[str, Any]) -> Any:
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

    if action in {"query_battery", "battery?"}:
        return tello.query_battery()

    if action in {"query_speed", "speed?"}:
        return tello.query_speed()

    if action in {"query_height", "height?"}:
        return tello.query_height()

    if action in {"query_temperature", "temperature?"}:
        return tello.query_temperature()

    if action in {"query_flight_time", "time?"}:
        return tello.query_flight_time()

    if action == "query_attitude":
        return tello.query_attitude()

    if action in {"query_barometer", "barometer?"}:
        return tello.query_barometer()

    if action == "query_acceleration":
        return tello.get_current_state()

    if action in {"query_distance_tof", "tof?"}:
        return tello.query_distance_tof()

    if action in {"query_wifi_snr", "wifi?"}:
        return tello.query_wifi_signal_noise_ratio()

    raise ValueError(f"Unsupported action for Tello execution: {action}")


def build_result_item(action: str, response: Any) -> Dict[str, Any]:
    result_item = {
        "action": action,
        "success": True,
        "response": response,
    }

    if action in {"query_battery", "battery?"}:
        result_item["value"] = response
        result_item["unit"] = "%"

    elif action in {"query_speed", "speed?"}:
        result_item["value"] = response
        result_item["unit"] = "cm/s"

    elif action in {"query_height", "height?"}:
        result_item["value"] = response
        result_item["unit"] = "cm"

    elif action in {"query_temperature", "temperature?"}:
        result_item["value"] = response
        result_item["unit"] = "°C"

    elif action in {"query_flight_time", "time?"}:
        result_item["value"] = response
        result_item["unit"] = "s"

    elif action in {"query_distance_tof", "tof?"}:
        result_item["value"] = response
        result_item["unit"] = "cm"

    elif action in {"query_wifi_snr", "wifi?"}:
        result_item["value"] = response
        result_item["unit"] = "SNR"

    elif action in {"query_barometer", "barometer?"}:
        result_item["value"] = response
        result_item["unit"] = "m"

    elif action == "streamon":
        result_item["value"] = "stream started"

    elif action == "streamoff":
        result_item["value"] = "stream stopped"

    return result_item


def execute_commands_with_tello(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    tello = Tello()

    results = []
    execution_results = []
    logs = []
    streaming = False

    try:
        logs.append("connect: starting")
        tello.connect()
        logs.append("connect: ok")

        battery = tello.query_battery()
        logs.append(f"battery: {battery}%")

        if battery < 20:
            final_state = safe_read_tello_state(tello, streaming=streaming)

            return {
                "success": False,
                "results": results,
                "execution_results": execution_results,
                "logs": logs,
                "error": "Battery too low for safe execution.",
                "final_state": final_state,
            }

        for command in commands:
            action = command["action"]

            response = execute_command_with_tello(tello, command)

            if action == "streamon":
                streaming = True

            if action == "streamoff":
                streaming = False

            result_item = build_result_item(action, response)

            results.append(result_item)
            execution_results.append(result_item)
            logs.append(f"{action}: {response}")

        final_state = safe_read_tello_state(tello, streaming=streaming)
        logs.append(f"final_state: {final_state}")

        return {
            "success": True,
            "results": results,
            "execution_results": execution_results,
            "logs": logs,
            "error": None,
            "final_state": final_state,
        }

    except Exception as error:
        logs.append(f"execution error: {error}")

        final_state = None

        try:
            final_state = safe_read_tello_state(tello, streaming=streaming)
        except Exception:
            pass

        return {
            "success": False,
            "results": results,
            "execution_results": execution_results,
            "logs": logs,
            "error": str(error),
            "final_state": final_state,
        }

    finally:
        try:
            tello.end()
            logs.append("end: ok")
        except Exception:
            pass