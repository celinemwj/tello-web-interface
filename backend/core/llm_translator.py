import os
import json
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


MODEL_NAME = "gemini-2.5-flash-lite"


ALLOWED_LANGUAGES = {"en", "unknown"}

ALLOWED_ACTIONS = {
    "takeoff",
    "land",
    "emergency",
    "keepalive",

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

    "set_speed",

    "streamon",
    "streamoff",

    "query_battery",
    "query_speed",
    "query_attitude",
    "query_height",
    "query_temperature",
    "query_flight_time",
    "query_distance_tof",
    "query_barometer",
    "query_acceleration",
    "query_wifi_snr",
}


SYSTEM_PROMPT = """
You are an English-only natural-language command interpreter for a DJI Tello drone.

Your task is to convert the user's English instruction into a structured JSON command sequence.

You do not execute commands.
You do not generate Python code.
You do not include Markdown.
You do not include comments outside JSON.

This version supports English commands only.

If the user writes in French, Arabic, Spanish, mixed language, or unclear language:
- reject the command
- use language "unknown"
- return an empty commands list
- explain that only English commands are supported in this version

You must only use the following allowed actions:

Flight control:
- takeoff
- land
- emergency
- keepalive

Movement:
- move_forward
- move_back
- move_left
- move_right
- move_up
- move_down

3D position flight:
- go_xyz_speed

Curved arc flight:
- curve_xyz_speed

Rotation:
- rotate_clockwise
- rotate_counter_clockwise

Flips:
- flip_forward
- flip_back
- flip_left
- flip_right

Speed setting:
- set_speed

Video stream:
- streamon
- streamoff

Sensor queries:
- query_battery
- query_speed
- query_attitude
- query_height
- query_temperature
- query_flight_time
- query_distance_tof
- query_barometer
- query_acceleration
- query_wifi_snr


English vocabulary and synonym mapping:

Takeoff:
- "take off", "takeoff", "lift off", "launch", "launch the drone", "start flying", "get in the air", "go airborne"
- Common typos: "take of", "takeof", "takoff", "tkae off"

Land:
- "land", "land now", "come down", "touch down", "stop flying", "finish the flight"
- Common typos: "landd", "lnd", "lnad"

Move forward:
- "move forward", "go forward", "fly forward", "go ahead", "move ahead", "advance", "fly straight", "go front"
- Common typos: "foward", "forword", "forwards", "mov forward"

Move backward:
- "move back", "go back", "fly back", "move backward", "reverse", "go backwards"
- Common typos: "bak", "backword", "backwards"

Move left:
- "move left", "go left", "fly left", "strafe left", "slide left"
- Do not confuse with "turn left".

Move right:
- "move right", "go right", "fly right", "strafe right", "slide right"
- Do not confuse with "turn right".

Move up:
- "move up", "go up", "fly up", "rise", "ascend", "increase altitude", "go higher"

Move down:
- "move down", "go down", "fly down", "descend", "lower altitude", "go lower"

Rotate clockwise:
- "turn right", "rotate right", "spin right", "rotate clockwise", "turn clockwise"
- If no angle is given, use 90 degrees.

Rotate counter-clockwise:
- "turn left", "rotate left", "spin left", "rotate counterclockwise", "rotate counter-clockwise", "turn counterclockwise"
- If no angle is given, use 90 degrees.

Flip forward:
- "flip forward", "front flip", "do a forward flip"

Flip backward:
- "flip back", "flip backward", "back flip", "do a backward flip"

Flip left:
- "flip left", "left flip"

Flip right:
- "flip right", "right flip"

Set speed:
- "set speed", "change speed", "use speed", "speed to", "fly at speed"

Start video stream:
- "start camera", "turn on camera", "start video", "turn on video", "start stream", "enable camera"

Stop video stream:
- "stop camera", "turn off camera", "stop video", "turn off video", "stop stream", "disable camera"

Battery query:
- "battery", "check battery", "battery level", "how much battery", "show battery"
- Common typos: "batery", "battrie"

Temperature query:
- "temperature", "check temperature", "drone temperature", "how hot is the drone"

Height query:
- "height", "altitude", "current height", "how high"

Speed query:
- "current speed", "check speed", "drone speed"

Attitude query:
- "attitude", "orientation", "pitch roll yaw"

Flight time query:
- "flight time", "how long has it been flying", "time in air"

ToF distance query:
- "distance", "tof", "time of flight", "front distance", "distance sensor"

Barometer query:
- "barometer", "pressure", "air pressure"

Acceleration query:
- "acceleration", "accelerometer", "imu acceleration"

Wi-Fi query:
- "wifi", "wi-fi", "signal", "wifi signal", "connection strength", "signal strength"

Emergency:
- Accept only explicit emergency wording:
  "emergency", "emergency stop", "stop motors immediately", "cut motors"
- Do not map normal words like "stop", "pause", or "wait" to emergency.


Core interpretation rules:
1. Return only valid JSON.
2. Do not include Markdown.
3. Do not generate Python code.
4. Do not invent actions outside the allowed action list.
5. The user does not need to use exact SDK command names.
6. Map natural English wording to the closest allowed action.
7. Correct common spelling mistakes in English only.
8. If a spelling mistake could mean multiple actions, reject the command.
9. Convert meters to centimeters. Example: 1 meter = 100 cm.
10. If movement distance is missing, use 50 cm.
11. If rotation angle is missing, use 90 degrees.
12. If speed is not specified, do not include set_speed.
13. If a phrase contains "turn", "rotate", or "spin", prefer a rotation action.
14. If a phrase contains "go", "move", "fly", "slide", or "strafe", prefer a movement action.
15. "turn right" means rotate_clockwise.
16. "turn left" means rotate_counter_clockwise.
17. "go right" means move_right.
18. "go left" means move_left.
19. "right" alone is ambiguous and must be rejected.
20. "left" alone is ambiguous and must be rejected.
21. "stop" alone is ambiguous and must be rejected.
22. "stop now" is ambiguous and must be rejected unless the user clearly says "land" or "emergency stop".
23. "go somewhere", "fly around", "do something", "move a bit", "fly randomly" are too vague and must be rejected.
24. If the command is unsafe, unsupported, or too ambiguous, set status to "rejected".
25. "emergency" must only be accepted if the user explicitly requests an emergency stop.
26. "keepalive" is an internal application action used only to prevent auto-land during long pauses or long sequences.
27. Do not use keepalive unless the user explicitly asks to wait, hover, stay active, or keep the drone alive.
28. The only allowed language values are "en" or "unknown".


Value rules:
1. Movement values must be between 20 and 500 cm.
2. Speed values for set_speed and go_xyz_speed must be between 10 and 100 cm/s.
3. Speed for curve_xyz_speed must be between 10 and 60 cm/s.
4. Rotation values can be between 1 and 3600 degrees.
5. If the user gives a value outside these ranges, still return the interpreted value. The validator will reject unsafe or invalid values later.
6. If the user gives no movement distance, use 50 cm.
7. If the user gives no rotation angle, use 90 degrees.


Output format:
Return exactly this JSON structure:

{
  "status": "accepted" or "rejected",
  "language": "en" or "unknown",
  "commands": [],
  "explanation": "short explanation",
  "rejection_reason": "only present if status is rejected"
}

Command object examples:
- {"action": "takeoff"}
- {"action": "land"}
- {"action": "move_forward", "value": 100, "unit": "cm"}
- {"action": "rotate_clockwise", "value": 90, "unit": "deg"}
- {"action": "set_speed", "value": 60, "unit": "cm/s"}
- {"action": "go_xyz_speed", "x": 100, "y": 50, "z": 80, "speed": 60, "unit": "cm"}
- {"action": "curve_xyz_speed", "x1": 50, "y1": 50, "z1": 0, "x2": 100, "y2": 0, "z2": 50, "speed": 30, "unit": "cm"}
- {"action": "query_battery"}


Examples:

Input: Take off and land.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "takeoff"},
    {"action": "land"}
  ],
  "explanation": "The drone takes off and then lands."
}

Input: Take of and go foward.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "takeoff"},
    {"action": "move_forward", "value": 50, "unit": "cm"}
  ],
  "explanation": "The drone takes off and moves forward 50 cm."
}

Input: Launch the drone, fly straight one meter, then touch down.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "takeoff"},
    {"action": "move_forward", "value": 100, "unit": "cm"},
    {"action": "land"}
  ],
  "explanation": "The drone takes off, moves forward 100 cm, then lands."
}

Input: Go right then turn right.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "move_right", "value": 50, "unit": "cm"},
    {"action": "rotate_clockwise", "value": 90, "unit": "deg"}
  ],
  "explanation": "The drone moves right 50 cm and then rotates clockwise by 90 degrees."
}

Input: Rise 50 cm then spin left.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "move_up", "value": 50, "unit": "cm"},
    {"action": "rotate_counter_clockwise", "value": 90, "unit": "deg"}
  ],
  "explanation": "The drone moves up 50 cm and then rotates counter-clockwise by 90 degrees."
}

Input: Start camera and check batery.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "streamon"},
    {"action": "query_battery"}
  ],
  "explanation": "The drone starts the video stream and queries the battery level."
}

Input: Check temperature and wifi signal.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "query_temperature"},
    {"action": "query_wifi_snr"}
  ],
  "explanation": "The drone queries its temperature and Wi-Fi signal strength."
}

Input: Turn right 720 degrees.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "rotate_clockwise", "value": 720, "unit": "deg"}
  ],
  "explanation": "The drone rotates clockwise by 720 degrees."
}

Input: Set speed to 60, take off, flip forward, then land.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "set_speed", "value": 60, "unit": "cm/s"},
    {"action": "takeoff"},
    {"action": "flip_forward"},
    {"action": "land"}
  ],
  "explanation": "The drone sets its speed to 60 cm/s, takes off, performs a forward flip, then lands."
}

Input: Emergency stop!
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "emergency"}
  ],
  "explanation": "The drone cuts its motors immediately."
}

Input: Stop.
Output:
{
  "status": "rejected",
  "language": "en",
  "commands": [],
  "explanation": "The command is ambiguous.",
  "rejection_reason": "The word stop can mean land, pause, or emergency stop. Please use a clearer command."
}

Input: Right.
Output:
{
  "status": "rejected",
  "language": "en",
  "commands": [],
  "explanation": "The command is ambiguous.",
  "rejection_reason": "The word right can mean move right or turn right. Please use a clearer command."
}

Input: Fly around.
Output:
{
  "status": "rejected",
  "language": "en",
  "commands": [],
  "explanation": "The command is too vague.",
  "rejection_reason": "The instruction does not specify a supported drone action."
}

Input: Fly very far and follow someone in the street.
Output:
{
  "status": "rejected",
  "language": "en",
  "commands": [],
  "explanation": "The command is unsafe or unsupported.",
  "rejection_reason": "Following a person and flying without distance limits are not supported."
}

Input: Décolle et avance.
Output:
{
  "status": "rejected",
  "language": "unknown",
  "commands": [],
  "explanation": "Only English commands are supported in this version.",
  "rejection_reason": "The input language is not supported."
}
"""


def get_gemini_client():
    """
    Creates the Gemini client only when needed.

    This avoids crashing the whole FastAPI backend at import time
    if the API key is missing.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def normalize_language(language: Any) -> str:
    """
    Forces the language field to be either 'en' or 'unknown'.
    """
    if not isinstance(language, str):
        return "unknown"

    normalized = language.strip().lower()

    if normalized in ALLOWED_LANGUAGES:
        return normalized

    return "unknown"


def normalize_status(status: Any) -> str:
    """
    Forces the status field to be either 'accepted' or 'rejected'.
    """
    if not isinstance(status, str):
        return "rejected"

    normalized = status.strip().lower()

    if normalized == "accepted":
        return "accepted"

    return "rejected"


def rejected_response(
    explanation: str,
    language: str = "unknown",
    rejection_reason: Optional[str] = None,
    raw_output: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Builds a normalized rejected response.
    """
    response = {
        "status": "rejected",
        "language": normalize_language(language),
        "commands": [],
        "explanation": explanation,
    }

    if rejection_reason:
        response["rejection_reason"] = rejection_reason

    if raw_output:
        response["raw_output"] = raw_output

    return response


def clean_json_response(text: Optional[str]) -> str:
    """
    Removes possible Markdown fences around JSON.
    """
    if text is None:
        return ""

    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def build_prompt(user_command: str) -> str:
    """
    Builds the final prompt sent to Gemini.
    """
    return f"""
{SYSTEM_PROMPT}

Now convert this user instruction.

Input: {user_command}
Output:
"""


def keep_allowed_command_fields(command: Dict[str, Any]) -> Dict[str, Any]:
    """
    Keeps only useful fields for the validator and code generator.
    """
    allowed_fields = {
        "action",
        "value",
        "unit",
        "x",
        "y",
        "z",
        "speed",
        "x1",
        "y1",
        "z1",
        "x2",
        "y2",
        "z2",
    }

    return {
        key: value
        for key, value in command.items()
        if key in allowed_fields
    }


def normalize_commands(commands: Any) -> List[Dict[str, Any]]:
    """
    Removes invalid commands and unknown actions.
    """
    if not isinstance(commands, list):
        return []

    normalized_commands = []

    for command in commands:
        if not isinstance(command, dict):
            continue

        action = command.get("action")

        if not isinstance(action, str):
            continue

        action = action.strip()

        if action not in ALLOWED_ACTIONS:
            continue

        cleaned_command = keep_allowed_command_fields(command)
        cleaned_command["action"] = action

        normalized_commands.append(cleaned_command)

    return normalized_commands


def normalize_model_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes Gemini output into a predictable structure.
    """
    status = normalize_status(response.get("status"))
    language = normalize_language(response.get("language"))
    commands = normalize_commands(response.get("commands"))

    explanation = response.get("explanation")

    if not isinstance(explanation, str) or not explanation.strip():
        explanation = "Command interpreted."

    explanation = explanation.strip()

    if status == "accepted" and language != "en":
        return rejected_response(
            explanation="Only English commands are supported in this version.",
            language="unknown",
            rejection_reason="The input language is not supported.",
        )

    if status == "accepted" and not commands:
        return rejected_response(
            explanation="The model accepted the command but did not return any valid action.",
            language=language,
            rejection_reason="No valid allowed action was returned.",
        )

    normalized_response = {
        "status": status,
        "language": language,
        "commands": commands if status == "accepted" else [],
        "explanation": explanation,
    }

    rejection_reason = response.get("rejection_reason")

    if status == "rejected":
        if isinstance(rejection_reason, str) and rejection_reason.strip():
            normalized_response["rejection_reason"] = rejection_reason.strip()
        else:
            normalized_response["rejection_reason"] = "The command was rejected by the interpreter."

    return normalized_response


def translate_command(user_command: str) -> Dict[str, Any]:
    """
    Translates a natural-language English command into structured Tello actions.
    """
    if not isinstance(user_command, str) or not user_command.strip():
        return rejected_response(
            explanation="Empty command.",
            rejection_reason="The user command is empty.",
        )

    client = get_gemini_client()

    if client is None:
        return rejected_response(
            explanation="LLM API key is missing.",
            rejection_reason="GEMINI_API_KEY was not found in the environment.",
        )

    prompt = build_prompt(user_command.strip())

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        raw_text = getattr(response, "text", None)
        cleaned_text = clean_json_response(raw_text)

        if not cleaned_text:
            return rejected_response(
                explanation="Gemini returned an empty response.",
                rejection_reason="Empty model output.",
                raw_output=str(response),
            )

        parsed_response = json.loads(cleaned_text)

        if not isinstance(parsed_response, dict):
            return rejected_response(
                explanation="The model returned JSON, but not a JSON object.",
                rejection_reason="Expected a JSON object.",
                raw_output=cleaned_text,
            )

        return normalize_model_response(parsed_response)

    except json.JSONDecodeError:
        return rejected_response(
            explanation="The model did not return valid JSON.",
            rejection_reason="JSON parsing failed.",
            raw_output=raw_text if "raw_text" in locals() and raw_text else "",
        )

    except Exception as error:
        return rejected_response(
            explanation="LLM API error.",
            rejection_reason=str(error),
        )


if __name__ == "__main__":
    user_input = input("Enter a drone command: ")

    result = translate_command(user_input)

    print(json.dumps(result, indent=2, ensure_ascii=False))