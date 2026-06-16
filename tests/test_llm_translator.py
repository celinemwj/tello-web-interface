import json
from backend.core.llm_translator import translate_command


TEST_CASES = [
    {
        "input": "take of and go foward",
        "expected_status": "accepted",
        "expected_language": "en",
        "expected_actions": ["takeoff", "move_forward"],
    },
    {
        "input": "launch the drone then fly straight",
        "expected_status": "accepted",
        "expected_language": "en",
        "expected_actions": ["takeoff", "move_forward"],
    },
    {
        "input": "go right then turn right",
        "expected_status": "accepted",
        "expected_language": "en",
        "expected_actions": ["move_right", "rotate_clockwise"],
    },
    {
        "input": "start camera and check batery",
        "expected_status": "accepted",
        "expected_language": "en",
        "expected_actions": ["streamon", "query_battery"],
    },
    {
        "input": "rise 50 cm then spin left",
        "expected_status": "accepted",
        "expected_language": "en",
        "expected_actions": ["move_up", "rotate_counter_clockwise"],
    },
    {
        "input": "stop",
        "expected_status": "rejected",
        "expected_language": "en",
        "expected_actions": [],
    },
    {
        "input": "right",
        "expected_status": "rejected",
        "expected_language": "en",
        "expected_actions": [],
    },
    {
        "input": "fly around",
        "expected_status": "rejected",
        "expected_language": "en",
        "expected_actions": [],
    },
    {
        "input": "Décolle et avance",
        "expected_status": "rejected",
        "expected_language": "unknown",
        "expected_actions": [],
    },
]


def get_actions(result):
    return [
        command.get("action")
        for command in result.get("commands", [])
    ]


def run_test_case(test_case):
    user_input = test_case["input"]

    result = translate_command(user_input)

    actual_status = result.get("status")
    actual_language = result.get("language")
    actual_actions = get_actions(result)

    expected_status = test_case["expected_status"]
    expected_language = test_case["expected_language"]
    expected_actions = test_case["expected_actions"]

    passed = (
        actual_status == expected_status
        and actual_language == expected_language
        and actual_actions == expected_actions
    )

    if passed:
        print(f"PASS - {user_input}")
        return True

    print(f"FAIL - {user_input}")
    print(f"Expected status: {expected_status}")
    print(f"Actual status:   {actual_status}")
    print(f"Expected language: {expected_language}")
    print(f"Actual language:   {actual_language}")
    print(f"Expected actions: {expected_actions}")
    print(f"Actual actions:   {actual_actions}")
    print("Full result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("-" * 80)

    return False


def main():
    passed_count = 0

    for test_case in TEST_CASES:
        if run_test_case(test_case):
            passed_count += 1

    total_count = len(TEST_CASES)

    print("=" * 80)
    print(f"Result: {passed_count}/{total_count} tests passed.")

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()