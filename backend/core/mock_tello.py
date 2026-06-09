"""
mock_tello.py

A lightweight software mock of a DJI Tello drone.

It does not simulate real drone physics.
It is used to test the software pipeline safely:

LLM output
→ validation
→ code generation
→ mock execution

before deploying on the real drone with DJITelloPy.
"""

from typing import Dict, Any, List


class MockTello:
    def __init__(self) -> None:
        self.is_connected = False
        self.is_flying = False
        self.streaming = False

        self.battery = 100
        self.speed = 50

        # Simple relative position in cm
        self.x = 0
        self.y = 0
        self.z = 0

        # Yaw angle in degrees
        self.yaw = 0

        self.flight_time = 0
        self.temperature = 25
        self.height = 0
        self.tof = 100
        self.wifi_snr = 90

        self.logs: List[str] = []

    def log(self, message: str) -> str:
        self.logs.append(message)
        return message

    # ── Connection ───────────────────────────────────────────────────────────

    def connect(self) -> str:
        self.is_connected = True
        return self.log("connect: ok")

    def end(self) -> str:
        self.is_connected = False
        self.is_flying = False
        self.streaming = False
        return self.log("end: ok")

    def ensure_connected(self) -> None:
        if not self.is_connected:
            raise RuntimeError("MockTello is not connected.")

    def ensure_flying(self) -> None:
        if not self.is_flying:
            raise RuntimeError("MockTello is not flying.")

    # ── Flight control ───────────────────────────────────────────────────────

    def takeoff(self) -> str:
        self.ensure_connected()

        if self.is_flying:
            raise RuntimeError("Drone is already flying.")

        self.is_flying = True
        self.z = 80
        self.height = 80
        self.battery -= 1

        return self.log("takeoff: ok")

    def land(self) -> str:
        self.ensure_connected()

        if not self.is_flying:
            raise RuntimeError("Drone is not flying.")

        self.is_flying = False
        self.z = 0
        self.height = 0
        self.battery -= 1

        return self.log("land: ok")

    def emergency(self) -> str:
        self.ensure_connected()

        self.is_flying = False
        self.z = 0
        self.height = 0

        return self.log("emergency: motors stopped")

    def send_keepalive(self) -> str:
        self.ensure_connected()

        if not self.is_flying:
            raise RuntimeError("keepalive requires the drone to be flying.")

        return self.log("keepalive: ok")

    # ── Movement ─────────────────────────────────────────────────────────────

    def move_forward(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.x += value
        self.battery -= 1

        return self.log(f"move_forward({value}): ok")

    def move_back(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.x -= value
        self.battery -= 1

        return self.log(f"move_back({value}): ok")

    def move_left(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.y -= value
        self.battery -= 1

        return self.log(f"move_left({value}): ok")

    def move_right(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.y += value
        self.battery -= 1

        return self.log(f"move_right({value}): ok")

    def move_up(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.z += value
        self.height = self.z
        self.battery -= 1

        return self.log(f"move_up({value}): ok")

    def move_down(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.z = max(0, self.z - value)
        self.height = self.z
        self.battery -= 1

        return self.log(f"move_down({value}): ok")

    # ── Advanced movement ────────────────────────────────────────────────────

    def go_xyz_speed(self, x: int, y: int, z: int, speed: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.x += x
        self.y += y
        self.z += z
        self.height = self.z
        self.speed = speed
        self.battery -= 2

        return self.log(f"go_xyz_speed(x={x}, y={y}, z={z}, speed={speed}): ok")

    def curve_xyz_speed(
        self,
        x1: int,
        y1: int,
        z1: int,
        x2: int,
        y2: int,
        z2: int,
        speed: int,
    ) -> str:
        self.ensure_connected()
        self.ensure_flying()

        # Lightweight approximation:
        # final position becomes the second waypoint.
        self.x += x2
        self.y += y2
        self.z += z2
        self.height = self.z
        self.speed = speed
        self.battery -= 3

        return self.log(
            f"curve_xyz_speed(x1={x1}, y1={y1}, z1={z1}, "
            f"x2={x2}, y2={y2}, z2={z2}, speed={speed}): ok"
        )

    # ── Rotation ─────────────────────────────────────────────────────────────

    def rotate_clockwise(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.yaw = (self.yaw + value) % 360
        self.battery -= 1

        return self.log(f"rotate_clockwise({value}): ok")

    def rotate_counter_clockwise(self, value: int) -> str:
        self.ensure_connected()
        self.ensure_flying()

        self.yaw = (self.yaw - value) % 360
        self.battery -= 1

        return self.log(f"rotate_counter_clockwise({value}): ok")

    # ── Flips ────────────────────────────────────────────────────────────────

    def flip_forward(self) -> str:
        self.ensure_connected()
        self.ensure_flying()
        self.battery -= 2
        return self.log("flip_forward: ok")

    def flip_back(self) -> str:
        self.ensure_connected()
        self.ensure_flying()
        self.battery -= 2
        return self.log("flip_back: ok")

    def flip_left(self) -> str:
        self.ensure_connected()
        self.ensure_flying()
        self.battery -= 2
        return self.log("flip_left: ok")

    def flip_right(self) -> str:
        self.ensure_connected()
        self.ensure_flying()
        self.battery -= 2
        return self.log("flip_right: ok")

    # ── Speed ────────────────────────────────────────────────────────────────

    def set_speed(self, value: int) -> str:
        self.ensure_connected()

        self.speed = value

        return self.log(f"set_speed({value}): ok")

    # ── Video stream ─────────────────────────────────────────────────────────

    def streamon(self) -> str:
        self.ensure_connected()

        self.streaming = True

        return self.log("streamon: ok")

    def streamoff(self) -> str:
        self.ensure_connected()

        self.streaming = False

        return self.log("streamoff: ok")

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_battery(self) -> int:
        self.ensure_connected()
        self.log(f"query_battery: {self.battery}%")
        return self.battery

    def get_speed(self) -> int:
        self.ensure_connected()
        self.log(f"query_speed: {self.speed} cm/s")
        return self.speed

    def get_height(self) -> int:
        self.ensure_connected()
        self.log(f"query_height: {self.height} cm")
        return self.height

    def get_temperature(self) -> int:
        self.ensure_connected()
        self.log(f"query_temperature: {self.temperature} °C")
        return self.temperature

    def get_flight_time(self) -> int:
        self.ensure_connected()
        self.log(f"query_flight_time: {self.flight_time} s")
        return self.flight_time

    def get_current_state(self) -> Dict[str, Any]:
        self.ensure_connected()

        state = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "height": self.height,
            "yaw": self.yaw,
            "battery": self.battery,
            "speed": self.speed,
            "temperature": self.temperature,
            "tof": self.tof,
            "wifi_snr": self.wifi_snr,
            "is_flying": self.is_flying,
            "streaming": self.streaming,
        }

        self.log(f"query_state: {state}")

        return state

    def get_barometer(self) -> float:
        self.ensure_connected()
        barometer = self.z / 100.0
        self.log(f"query_barometer: {barometer} m")
        return barometer

    def get_distance_tof(self) -> int:
        self.ensure_connected()
        self.log(f"query_distance_tof: {self.tof} cm")
        return self.tof

    def query_wifi_signal_noise_ratio(self) -> int:
        self.ensure_connected()
        self.log(f"query_wifi_snr: {self.wifi_snr}")
        return self.wifi_snr


# ── Command execution helper ────────────────────────────────────────────────

def execute_command(mock: MockTello, command: Dict[str, Any]) -> Any:
    """
    Execute one validated command on MockTello.
    """
    action = command["action"]

    if action == "takeoff":
        return mock.takeoff()

    if action == "land":
        return mock.land()

    if action == "emergency":
        return mock.emergency()

    if action == "keepalive":
        return mock.send_keepalive()

    if action == "move_forward":
        return mock.move_forward(command["value"])

    if action == "move_back":
        return mock.move_back(command["value"])

    if action == "move_left":
        return mock.move_left(command["value"])

    if action == "move_right":
        return mock.move_right(command["value"])

    if action == "move_up":
        return mock.move_up(command["value"])

    if action == "move_down":
        return mock.move_down(command["value"])

    if action == "go_xyz_speed":
        return mock.go_xyz_speed(
            command["x"],
            command["y"],
            command["z"],
            command["speed"],
        )

    if action == "curve_xyz_speed":
        return mock.curve_xyz_speed(
            command["x1"],
            command["y1"],
            command["z1"],
            command["x2"],
            command["y2"],
            command["z2"],
            command["speed"],
        )

    if action == "rotate_clockwise":
        return mock.rotate_clockwise(command["value"])

    if action == "rotate_counter_clockwise":
        return mock.rotate_counter_clockwise(command["value"])

    if action == "flip_forward":
        return mock.flip_forward()

    if action == "flip_back":
        return mock.flip_back()

    if action == "flip_left":
        return mock.flip_left()

    if action == "flip_right":
        return mock.flip_right()

    if action == "set_speed":
        return mock.set_speed(command["value"])

    if action == "streamon":
        return mock.streamon()

    if action == "streamoff":
        return mock.streamoff()

    if action == "query_battery":
        return mock.get_battery()

    if action == "query_speed":
        return mock.get_speed()

    if action == "query_height":
        return mock.get_height()

    if action == "query_temperature":
        return mock.get_temperature()

    if action == "query_flight_time":
        return mock.get_flight_time()

    if action == "query_attitude":
        return mock.get_current_state()

    if action == "query_barometer":
        return mock.get_barometer()

    if action == "query_acceleration":
        return mock.get_current_state()

    if action == "query_distance_tof":
        return mock.get_distance_tof()

    if action == "query_wifi_snr":
        return mock.query_wifi_signal_noise_ratio()

    raise ValueError(f"Unsupported mock action: {action}")


def execute_commands(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute a list of validated commands on MockTello.
    """
    mock = MockTello()
    execution_results = []

    try:
        mock.connect()

        for command in commands:
            result = execute_command(mock, command)
            execution_results.append(result)

        final_state = mock.get_current_state()
        mock.end()

        return {
            "success": True,
            "execution_results": execution_results,
            "logs": mock.logs,
            "final_state": final_state,
        }

    except Exception as error:
        return {
            "success": False,
            "execution_results": execution_results,
            "logs": mock.logs,
            "error": str(error),
            "final_state": mock.get_current_state() if mock.is_connected else None,
        }


if __name__ == "__main__":
    import json

    sample_commands = [
        {"action": "takeoff"},
        {"action": "move_forward", "value": 100},
        {"action": "rotate_clockwise", "value": 90},
        {"action": "land"},
    ]

    result = execute_commands(sample_commands)
    print(json.dumps(result, indent=2, ensure_ascii=False))