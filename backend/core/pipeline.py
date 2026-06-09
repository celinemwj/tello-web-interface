import json
from typing import Dict, Any

from backend.core.llm_translator import translate_command
from backend.core.command_validator import validate_and_report
from backend.core.code_generator import (
    generate_python_code,
    execute_commands_with_tello,
)
from backend.core.mock_tello import execute_commands as execute_mock_commands

def run_pipeline(user_command: str, execution_mode: str = "mock") -> Dict[str, Any]:
    """
    Run the full core pipeline.

    Steps:
    1. Natural language command -> LLM JSON
    2. Validate JSON commands
    3. Generate Python DJITelloPy code for display
    4. Execute commands:
       - mock mode: MockTello
       - real mode: real DJI Tello through DJITelloPy

    execution_mode:
        - "mock": safe software simulation
        - "real": real drone execution, only when PC is connected to Tello Wi-Fi
    """

    # 1. LLM translation
    llm_output = translate_command(user_command)

    # 2. Validation
    validation_result = validate_and_report(llm_output)

    if not validation_result["valid"]:
        return {
            "success": False,
            "step": "validation",
            "execution_mode": execution_mode,
            "user_command": user_command,
            "llm_output": llm_output,
            "validation": validation_result,
            "generated_code": None,
            "execution": None,
        }

    commands = validation_result["commands"]

    # 3. Generate Python code for educational display
    generated_code = generate_python_code(commands)

    # 4. Execute according to selected mode
    if execution_mode == "mock":
        execution_result = execute_mock_commands(commands)

    elif execution_mode == "real":
        execution_result = execute_commands_with_tello(commands)

    else:
        return {
            "success": False,
            "step": "execution_mode",
            "execution_mode": execution_mode,
            "user_command": user_command,
            "llm_output": llm_output,
            "validation": validation_result,
            "generated_code": generated_code,
            "execution": None,
            "error": f"Unsupported execution mode: {execution_mode}",
        }

    return {
        "success": execution_result["success"],
        "step": "completed" if execution_result["success"] else "execution",
        "execution_mode": execution_mode,
        "user_command": user_command,
        "llm_output": llm_output,
        "validation": validation_result,
        "generated_code": generated_code,
        "execution": execution_result,
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