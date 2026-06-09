import os
import json
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash-lite"


SYSTEM_PROMPT = """
You are a command interpreter for a DJI Tello drone.

Your task is to convert the user's natural-language instruction into a structured JSON command sequence.

You must only use the following allowed actions:

Flight control
- takeoff
- land
- emergency
- keepalive

Movement
- move_forward(value in cm)
- move_back(value in cm)
- move_left(value in cm)
- move_right(value in cm)
- move_up(value in cm)
- move_down(value in cm)

3D position flight
- go_xyz_speed(x, y, z, speed)

Curved arc flight
- curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)

Rotation
- rotate_clockwise(value in degrees)
- rotate_counter_clockwise(value in degrees)

Flips
- flip_forward
- flip_back
- flip_left
- flip_right

Speed setting
- set_speed(value in cm/s)

Video stream
- streamon
- streamoff

Sensor queries
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

Rules:
1. Return only valid JSON.
2. Do not include Markdown.
3. Do not generate Python code.
4. Do not invent actions outside the list above.
5. Convert meters to centimeters. Example: 1 m = 100 cm.
6. Convert "turn right" to rotate_clockwise.
7. Convert "turn left" to rotate_counter_clockwise.
8. If rotation angle is not specified, use 90 degrees.
9. If movement distance is not specified, use 50 cm.
10. If speed is not specified, do not include a set_speed action.
11. Movement values must be between 20 and 500 cm.
12. Speed values for set_speed and go_xyz_speed must be between 10 and 100 cm/s.
13. Speed for curve_xyz_speed must be between 10 and 60 cm/s.
14. Rotation values can be between 1 and 3600 degrees.
15. If the command is unsupported, unsafe, or too ambiguous, set status to "rejected".
16. "emergency" must only be accepted if the user explicitly requests an emergency stop.
17. "keepalive" is an internal application action used only to prevent auto-land during long pauses or long sequences.
18. Do not execute the command.
19. Do not include comments outside the JSON.
20. The user may make spelling mistakes, omit accents, or use informal wording. If the intended command is clear, infer the closest logical allowed action.
21. Correct common spelling mistakes in English and French before mapping the instruction to actions.
22. If a misspelled word could correspond to multiple different actions, choose the safest interpretation or set status to "rejected".
23. Do not invent a new action because of a spelling mistake. Always map to the closest allowed action.
24. The only allowed language values are "en", "fr", or "unknown". Never output another language code.

The output must follow exactly this structure:

{
  "status": "accepted" or "rejected",
  "language": "en" or "fr" or "unknown",
  "commands": [
    {"action": "takeoff"},
    {"action": "move_forward", "value": 100, "unit": "cm"},
    {"action": "go_xyz_speed", "x": 100, "y": 50, "z": 30, "speed": 50, "unit": "cm"},
    {"action": "curve_xyz_speed", "x1": 50, "y1": 50, "z1": 0, "x2": 100, "y2": 0, "z2": 50, "speed": 30, "unit": "cm"},
    {"action": "query_battery"},
    {"action": "keepalive"}
  ],
  "explanation": "short explanation",
  "rejection_reason": "only present if status is rejected"
}

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

Input: Décolle, avance d'un mètre puis atterris.
Output:
{
  "status": "accepted",
  "language": "fr",
  "commands": [
    {"action": "takeoff"},
    {"action": "move_forward", "value": 100, "unit": "cm"},
    {"action": "land"}
  ],
  "explanation": "Le drone décolle, avance de 100 cm puis atterrit."
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

Input: Take off, fly to position 100 50 80 at speed 60, then land.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "takeoff"},
    {"action": "go_xyz_speed", "x": 100, "y": 50, "z": 80, "speed": 60, "unit": "cm"},
    {"action": "land"}
  ],
  "explanation": "The drone takes off, flies to relative position x=100 y=50 z=80 cm at 60 cm/s, then lands."
}

Input: Fly a curve through 50 50 0 then 100 0 50 at 30 cm/s.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "curve_xyz_speed", "x1": 50, "y1": 50, "z1": 0, "x2": 100, "y2": 0, "z2": 50, "speed": 30, "unit": "cm"}
  ],
  "explanation": "The drone flies a curved arc through two waypoints at 30 cm/s."
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
  "explanation": "The drone sets speed to 60 cm/s, takes off, performs a forward flip, then lands."
}

Input: Turn on the camera and check battery.
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

Input: Check the battery, temperature and wifi signal.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "query_battery"},
    {"action": "query_temperature"},
    {"action": "query_wifi_snr"}
  ],
  "explanation": "The drone queries battery, temperature and Wi-Fi signal-to-noise ratio."
}

Input: Check acceleration.
Output:
{
  "status": "accepted",
  "language": "en",
  "commands": [
    {"action": "query_acceleration"}
  ],
  "explanation": "The drone queries IMU acceleration data."
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

Input: Fly very far and follow someone in the street.
Output:
{
  "status": "rejected",
  "language": "en",
  "commands": [],
  "explanation": "The command is unsafe or unsupported for this drone control system.",
  "rejection_reason": "follow_person and unlimited range are not supported actions."
}
"""


def clean_json_response(text: str) -> str:

    if text is None:
        return ""

    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def build_prompt(user_command: str) -> str:
    """
    Builds the final prompt sent to Gemini.
    """
    return f"""
{SYSTEM_PROMPT}

Now convert this user instruction:

Input: {user_command}
Output:
"""


def translate_command(user_command: str) -> Dict[str, Any]:
    """
    Sends a natural-language drone instruction to Gemini
    and returns a Python dictionary containing structured Tello actions.
    """
    if not user_command or not user_command.strip():
        return {
            "status": "rejected",
            "language": "unknown",
            "commands": [],
            "explanation": "Empty command."
        }

    prompt = build_prompt(user_command)

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
            return {
                "status": "rejected",
                "language": "unknown",
                "commands": [],
                "explanation": "Gemini returned an empty response.",
                "raw_response": str(response)
            }

        parsed_response = json.loads(cleaned_text)
        return parsed_response

    except json.JSONDecodeError:
        return {
            "status": "rejected",
            "language": "unknown",
            "commands": [],
            "explanation": "The model did not return valid JSON.",
            "raw_output": raw_text if "raw_text" in locals() else ""
        }

    except Exception as error:
        return {
            "status": "rejected",
            "language": "unknown",
            "commands": [],
            "explanation": f"LLM API error: {str(error)}"
        }


if __name__ == "__main__":
    user_input = input("Enter a drone command: ")

    result = translate_command(user_input)

    print(json.dumps(result, indent=2, ensure_ascii=False))