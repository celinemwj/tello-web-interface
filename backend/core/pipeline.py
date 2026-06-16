import json
from typing import Any, Dict

from backend.core.llm_translator import translate_command
from backend.core.command_validator import validate_and_report
from backend.core.code_generator import (
    generate_python_code,
    execute_commands_with_tello,
)
from backend.core.mock_tello import execute_commands as execute_mock_commands


SUPPORTED_EXECUTION_MODES = {"mock", "real"}


def build_error_response(
    *,
    step: str,
    user_command: str,
    execution_mode: str,
    message: str,
    llm_output: Dict[str, Any] | None = None,
    validation: Dict[str, Any] | None = None,
    generated_code: str | None = None,
    execution: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Builds a consistent error response for the frontend.
    """
    return {
        "success": False,
        "step": step,
        "execution_mode": execution_mode,
        "user_command": user_command,
        "llm_output": llm_output,
        "validation": validation,
        "generated_code": generated_code,
        "execution": execution,
        "error": message,
    }


def normalize_execution_mode(execution_mode: str) -> str:
    """
    Normalizes the execution mode.
    Default mode is mock.
    """
    if not isinstance(execution_mode, str):
        return "mock"

    normalized_mode = execution_mode.strip().lower()

    if normalized_mode in SUPPORTED_EXECUTION_MODES:
        return normalized_mode

    return "unsupported"


def run_pipeline(user_command: str, execution_mode: str = "mock") -> Dict[str, Any]:
    """
    Run the full core pipeline.

    Steps:
    1. Natural language command -> structured JSON commands
    2. Validate structured commands
    3. Generate Python DJITelloPy code for educational display
    4. Execute commands:
       - mock mode: MockTello
       - real mode: real DJI Tello through DJITelloPy

    execution_mode:
        - "mock": safe software simulation
        - "real": real drone execution, only when PC is connected to Tello Wi-Fi
    """

    mode = normalize_execution_mode(execution_mode)

    if mode == "unsupported":
        return build_error_response(
            step="execution_mode",
            user_command=user_command,
            execution_mode=execution_mode,
            message=f"Unsupported execution mode: {execution_mode}",
        )

    if not isinstance(user_command, str) or not user_command.strip():
        return build_error_response(
            step="input",
            user_command=user_command,
            execution_mode=mode,
            message="Empty or invalid user command.",
        )

    user_command = user_command.strip()

    # 1. LLM translation
    try:
        llm_output = translate_command(user_command)

    except Exception as error:
        return build_error_response(
            step="translation",
            user_command=user_command,
            execution_mode=mode,
            message=f"Translation step failed: {str(error)}",
        )

    # Stop early if the translator rejected the command.
    if llm_output.get("status") != "accepted":
        return build_error_response(
            step="translation",
            user_command=user_command,
            execution_mode=mode,
            message=llm_output.get(
                "rejection_reason",
                "The command was rejected by the translator.",
            ),
            llm_output=llm_output,
        )

    # 2. Validation
    try:
        validation_result = validate_and_report(llm_output)

    except Exception as error:
        return build_error_response(
            step="validation",
            user_command=user_command,
            execution_mode=mode,
            message=f"Validation step failed: {str(error)}",
            llm_output=llm_output,
        )

    if not validation_result.get("valid", False):
        return build_error_response(
            step="validation",
            user_command=user_command,
            execution_mode=mode,
            message="The command sequence failed validation.",
            llm_output=llm_output,
            validation=validation_result,
        )

    commands = validation_result.get("commands", [])

    # 3. Generate Python code for educational display
    try:
        generated_code = generate_python_code(commands)

    except Exception as error:
        return build_error_response(
            step="code_generation",
            user_command=user_command,
            execution_mode=mode,
            message=f"Code generation step failed: {str(error)}",
            llm_output=llm_output,
            validation=validation_result,
        )

    # 4. Execute according to selected mode
    try:
        if mode == "mock":
            execution_result = execute_mock_commands(commands)

        elif mode == "real":
            execution_result = execute_commands_with_tello(commands)

    except Exception as error:
        return build_error_response(
            step="execution",
            user_command=user_command,
            execution_mode=mode,
            message=f"Execution step failed: {str(error)}",
            llm_output=llm_output,
            validation=validation_result,
            generated_code=generated_code,
        )

    return {
        "success": execution_result.get("success", False),
        "step": "completed" if execution_result.get("success", False) else "execution",
        "execution_mode": mode,
        "user_command": user_command,
        "llm_output": llm_output,
        "validation": validation_result,
        "generated_code": generated_code,
        "execution": execution_result,
        "error": None if execution_result.get("success", False) else "Execution failed.",
    }


if __name__ == "__main__":
    user_input = input("Enter a drone command: ")

    print("\nExecution modes:")
    print("1. mock  -> safe software simulation")
    print("2. real  -> real DJI Tello execution")

    mode = input("Choose execution mode [mock/real]: ").strip().lower()

    if mode not in {"mock", "real"}:
        mode = "mock"

    if mode == "real":
        print("\nWARNING: real mode will send commands to the physical DJI Tello.")
        print("Use it only when the PC is connected to the Tello Wi-Fi and the area is safe.")

        confirmation = input("Type CONFIRM_REAL to continue: ").strip()

        if confirmation != "CONFIRM_REAL":
            print("Real execution cancelled. Running in mock mode instead.")
            mode = "mock"

    result = run_pipeline(user_input, execution_mode=mode)

    print(json.dumps(result, indent=2, ensure_ascii=False))