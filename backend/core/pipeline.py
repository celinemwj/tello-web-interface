import json
from typing import Dict, Any, List

from backend.core.llm_translator import translate_command
from backend.core.command_validator import validate_and_report
from backend.core.code_generator import generate_python_code, execute_commands_with_tello
from backend.core.mock_tello import execute_commands as execute_mock_commands


PASSIVE_REAL_ACTIONS = {
    "battery?",
    "speed?",
    "height?",
    "temperature?",
    "time?",
    "tof?",
    "wifi?",
    "barometer?",

    "query_battery",
    "query_speed",
    "query_height",
    "query_temperature",
    "query_flight_time",
    "query_distance_tof",
    "query_wifi_snr",
    "query_barometer",
    "query_attitude",
    "query_acceleration",
}


FIRST_FLIGHT_ACTIONS = {
    "takeoff",
    "land",

    "battery?",
    "query_battery",

    "move_up",
    "move_down",
    "move_forward",
    "move_back",
    "move_left",
    "move_right",

    "rotate_clockwise",
    "rotate_counter_clockwise",
}


MAX_FIRST_FLIGHT_DISTANCE_CM = 30
MAX_FIRST_FLIGHT_ROTATION_DEG = 45


def build_error_response(
    execution_mode: str,
    error: str,
    llm_output: Dict[str, Any] | None = None,
    validation_result: Dict[str, Any] | None = None,
    generated_code: str | None = None,
) -> Dict[str, Any]:
    return {
        "success": False,
        "execution_mode": execution_mode,
        "llm_output": llm_output,
        "validation": validation_result,
        "generated_code": generated_code,
        "execution": None,
        "error": error,
    }


def normalize_execution_mode(execution_mode: str) -> str:
    if not execution_mode:
        return "mock"

    return execution_mode.strip().lower()


def find_unsafe_real_safe_actions(commands: List[Dict[str, Any]]) -> List[str]:
    unsafe_actions = []

    for command in commands:
        action = command.get("action")

        if action not in PASSIVE_REAL_ACTIONS:
            unsafe_actions.append(action)

    return unsafe_actions


def find_unsafe_first_flight_actions(commands: List[Dict[str, Any]]) -> List[str]:
    unsafe_actions = []

    for command in commands:
        action = command.get("action")

        if action not in FIRST_FLIGHT_ACTIONS:
            unsafe_actions.append(action)

    return unsafe_actions


def validate_first_flight_sequence(commands: List[Dict[str, Any]]) -> List[str]:
    errors = []

    actions = [command.get("action") for command in commands]

    if not actions:
        errors.append("No command was generated.")
        return errors

    movement_actions = {
        "move_up",
        "move_down",
        "move_forward",
        "move_back",
        "move_left",
        "move_right",
    }

    rotation_actions = {
        "rotate_clockwise",
        "rotate_counter_clockwise",
    }

    flight_actions = {
        "takeoff",
        "land",
        *movement_actions,
        *rotation_actions,
    }

    has_flight_action = any(action in flight_actions for action in actions)

    if has_flight_action:
        if "takeoff" not in actions:
            errors.append("Flight commands must start with takeoff.")

        if "land" not in actions:
            errors.append("Flight commands must end with land.")

    if "takeoff" in actions and "land" in actions:
        takeoff_index = actions.index("takeoff")
        land_index = actions.index("land")

        if land_index < takeoff_index:
            errors.append("Landing cannot happen before takeoff.")

        for index, action in enumerate(actions):
            if action in movement_actions or action in rotation_actions:
                if index < takeoff_index or index > land_index:
                    errors.append(
                        f"{action} must happen after takeoff and before land."
                    )

    for command in commands:
        action = command.get("action")
        value = command.get("value")

        if action in movement_actions:
            if value is None:
                errors.append(f"{action} requires a distance value.")

            elif value > MAX_FIRST_FLIGHT_DISTANCE_CM:
                errors.append(
                    f"{action} is limited to {MAX_FIRST_FLIGHT_DISTANCE_CM} cm "
                    f"in first flight mode. Requested: {value} cm."
                )

            elif value <= 0:
                errors.append(f"{action} distance must be positive.")

        if action in rotation_actions:
            if value is None:
                errors.append(f"{action} requires an angle value.")

            elif value > MAX_FIRST_FLIGHT_ROTATION_DEG:
                errors.append(
                    f"{action} is limited to {MAX_FIRST_FLIGHT_ROTATION_DEG} degrees "
                    f"in first flight mode. Requested: {value} degrees."
                )

            elif value <= 0:
                errors.append(f"{action} angle must be positive.")

    return errors


def run_pipeline(user_command: str, execution_mode: str = "mock") -> Dict[str, Any]:
    execution_mode = normalize_execution_mode(execution_mode)

    if execution_mode not in {"mock", "real", "real_safe", "real_first_flight"}:
        return build_error_response(
            execution_mode=execution_mode,
            error=f"Unsupported execution mode: {execution_mode}",
        )

    try:
        llm_output = translate_command(user_command)

    except Exception as error:
        print("LLM API ERROR DETAIL:", repr(error))

        return build_error_response(
            execution_mode=execution_mode,
            error=f"LLM translation error: {error}",
        )

    if llm_output.get("status") != "accepted":
        return build_error_response(
            execution_mode=execution_mode,
            error=llm_output.get(
                "explanation",
                "Command rejected by the LLM translator.",
            ),
            llm_output=llm_output,
        )

    try:
        validation_result = validate_and_report(llm_output)

    except Exception as error:
        return build_error_response(
            execution_mode=execution_mode,
            error=f"Validation error: {error}",
            llm_output=llm_output,
        )

    if not validation_result.get("valid"):
        return build_error_response(
            execution_mode=execution_mode,
            error="Command rejected by validator.",
            llm_output=llm_output,
            validation_result=validation_result,
        )

    commands = validation_result.get("commands", [])

    if execution_mode == "real_safe":
        unsafe_actions = find_unsafe_real_safe_actions(commands)

        if unsafe_actions:
            return build_error_response(
                execution_mode=execution_mode,
                error=(
                    "Blocked by real_safe mode. "
                    f"Unsafe actions are not allowed: {unsafe_actions}"
                ),
                llm_output=llm_output,
                validation_result={
                    "valid": False,
                    "errors": [
                        "real_safe mode only allows passive telemetry commands.",
                        f"Blocked actions: {unsafe_actions}",
                    ],
                    "commands": commands,
                },
            )

    if execution_mode == "real_first_flight":
        unsafe_actions = find_unsafe_first_flight_actions(commands)
        sequence_errors = validate_first_flight_sequence(commands)

        errors = []

        if unsafe_actions:
            errors.append(
                "First flight mode only allows takeoff, land, battery check, "
                "small movements, and small rotations."
            )
            errors.append(f"Blocked actions: {unsafe_actions}")

        errors.extend(sequence_errors)

        if errors:
            return build_error_response(
                execution_mode=execution_mode,
                error="Unsafe command blocked by first flight mode.",
                llm_output=llm_output,
                validation_result={
                    "valid": False,
                    "errors": errors,
                    "commands": commands,
                },
            )

    try:
        generated_code = generate_python_code(commands)

    except Exception as error:
        return build_error_response(
            execution_mode=execution_mode,
            error=f"Code generation error: {error}",
            llm_output=llm_output,
            validation_result=validation_result,
        )

    try:
        if execution_mode == "mock":
            execution_result = execute_mock_commands(commands)

        elif execution_mode == "real_safe":
            execution_result = execute_commands_with_tello(commands)

        elif execution_mode == "real_first_flight":
            execution_result = execute_commands_with_tello(commands)

        elif execution_mode == "real":
            execution_result = execute_commands_with_tello(commands)

        else:
            return build_error_response(
                execution_mode=execution_mode,
                error=f"Unsupported execution mode during execution: {execution_mode}",
                llm_output=llm_output,
                validation_result=validation_result,
                generated_code=generated_code,
            )

    except Exception as error:
        return build_error_response(
            execution_mode=execution_mode,
            error=f"Execution error: {error}",
            llm_output=llm_output,
            validation_result=validation_result,
            generated_code=generated_code,
        )

    return {
        "success": True,
        "execution_mode": execution_mode,
        "llm_output": llm_output,
        "validation": validation_result,
        "generated_code": generated_code,
        "execution": execution_result,
        "error": None,
    }


if __name__ == "__main__":
    while True:
        user_input = input("\nEnter a drone command: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        result = run_pipeline(user_input, execution_mode="real_first_flight")
        print(json.dumps(result, indent=2))