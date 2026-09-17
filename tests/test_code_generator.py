"""
Tests unitaires du generateur de code Python et des regles de securite
du mode real_first_flight.

Comme tests/test_command_validator.py, ces tests sont deterministes et ne
necessitent ni cle API ni drone.

    pytest tests/
"""

import pytest

from backend.core.code_generator import (
    generate_command_line,
    generate_python_code,
    build_result_item,
)
from backend.core.pipeline import (
    find_unsafe_first_flight_actions,
    validate_first_flight_sequence,
    normalize_execution_mode,
    MAX_FIRST_FLIGHT_DISTANCE_CM,
    MAX_FIRST_FLIGHT_ROTATION_DEG,
)


# ------------------------------------------------------------
# Generation de lignes de code
# ------------------------------------------------------------

def test_action_sans_argument():
    assert generate_command_line({"action": "takeoff"}) == "tello.takeoff()"
    assert generate_command_line({"action": "land"}) == "tello.land()"


def test_action_avec_valeur():
    line = generate_command_line({"action": "move_forward", "value": 100})

    assert line == "tello.move_forward(100)"


def test_rotation_avec_valeur():
    line = generate_command_line({"action": "rotate_clockwise", "value": 90})

    assert line == "tello.rotate_clockwise(90)"


def test_go_xyz_speed():
    line = generate_command_line({
        "action": "go_xyz_speed",
        "x": 50, "y": 0, "z": 20, "speed": 30,
    })

    assert line == "tello.go_xyz_speed(50, 0, 20, 30)"


def test_action_non_supportee_leve_une_erreur():
    with pytest.raises(ValueError):
        generate_command_line({"action": "teleport"})


# ------------------------------------------------------------
# Script complet
# ------------------------------------------------------------

def test_script_complet_a_la_bonne_structure():
    code = generate_python_code([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 50},
        {"action": "land"},
    ])

    lines = code.split("\n")

    assert lines[0] == "from djitellopy import Tello"
    assert "tello = Tello()" in lines
    assert "tello.connect()" in lines
    assert "tello.takeoff()" in lines
    assert "tello.move_forward(50)" in lines
    assert "tello.land()" in lines
    assert lines[-1] == "tello.end()"


def test_script_respecte_l_ordre_des_commandes():
    code = generate_python_code([
        {"action": "takeoff"},
        {"action": "move_up", "value": 30},
        {"action": "land"},
    ])

    assert code.index("tello.takeoff()") < code.index("tello.move_up(30)")
    assert code.index("tello.move_up(30)") < code.index("tello.land()")


# ------------------------------------------------------------
# Formatage des resultats
# ------------------------------------------------------------

def test_resultat_batterie_porte_une_unite():
    item = build_result_item("query_battery", 87)

    assert item["success"] is True
    assert item["value"] == 87
    assert item["unit"] == "%"


def test_resultat_hauteur_en_cm():
    item = build_result_item("query_height", 120)

    assert item["unit"] == "cm"


def test_resultat_takeoff_sans_unite():
    item = build_result_item("takeoff", True)

    assert item["action"] == "takeoff"
    assert "unit" not in item


# ------------------------------------------------------------
# Mode real_first_flight : actions autorisees
# ------------------------------------------------------------

def test_actions_de_base_sont_autorisees():
    unsafe = find_unsafe_first_flight_actions([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 30},
        {"action": "land"},
    ])

    assert unsafe == []


def test_flip_est_bloque_en_first_flight():
    unsafe = find_unsafe_first_flight_actions([
        {"action": "takeoff"},
        {"action": "flip_forward"},
        {"action": "land"},
    ])

    assert "flip_forward" in unsafe


def test_emergency_est_bloque_en_first_flight():
    unsafe = find_unsafe_first_flight_actions([{"action": "emergency"}])

    assert "emergency" in unsafe


# ------------------------------------------------------------
# Mode real_first_flight : sequence et bornes
# ------------------------------------------------------------

def test_sequence_first_flight_correcte():
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 30},
        {"action": "land"},
    ])

    assert errors == []


def test_vol_sans_takeoff_est_refuse():
    errors = validate_first_flight_sequence([
        {"action": "move_forward", "value": 30},
        {"action": "land"},
    ])

    assert any("must start with takeoff" in error for error in errors)


def test_vol_sans_land_est_refuse():
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 30},
    ])

    assert any("must end with land" in error for error in errors)


def test_land_avant_takeoff_est_refuse():
    errors = validate_first_flight_sequence([
        {"action": "land"},
        {"action": "takeoff"},
    ])

    assert len(errors) > 0


def test_distance_au_dessus_de_la_limite_est_refusee():
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "move_forward", "value": MAX_FIRST_FLIGHT_DISTANCE_CM + 1},
        {"action": "land"},
    ])

    assert any("is limited to" in error for error in errors)


def test_distance_par_defaut_du_llm_passe_la_limite():
    """
    Le prompt applique 50 cm par defaut si l'utilisateur ne precise pas de
    distance. Ce test garantit que la limite du mode first flight reste
    coherente avec ce defaut, sinon toute commande sans distance serait
    systematiquement rejetee.
    """
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 50},
        {"action": "land"},
    ])

    assert errors == []


def test_angle_par_defaut_du_llm_passe_la_limite():
    """Meme raisonnement pour l'angle par defaut de 90 degres."""
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "rotate_clockwise", "value": 90},
        {"action": "land"},
    ])

    assert errors == []


def test_angle_au_dessus_de_la_limite_est_refuse():
    errors = validate_first_flight_sequence([
        {"action": "takeoff"},
        {"action": "rotate_clockwise", "value": MAX_FIRST_FLIGHT_ROTATION_DEG + 1},
        {"action": "land"},
    ])

    assert any("is limited to" in error for error in errors)


def test_sequence_vide_est_refusee():
    errors = validate_first_flight_sequence([])

    assert len(errors) > 0


# ------------------------------------------------------------
# Normalisation du mode
# ------------------------------------------------------------

def test_normalisation_du_mode():
    assert normalize_execution_mode("  MOCK ") == "mock"
    assert normalize_execution_mode("Real_First_Flight") == "real_first_flight"
    assert normalize_execution_mode("") == "mock"
