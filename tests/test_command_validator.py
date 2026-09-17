"""
Tests unitaires du validateur de commandes.

Ces tests sont entierement deterministes : ils n'appellent ni l'API Gemini,
ni le drone. Ils peuvent donc etre lances par un correcteur sans cle API et
sans materiel.

    pytest tests/
"""

from backend.core.command_validator import validate, validate_and_report


def accepted(commands):
    """Construit une sortie LLM acceptee avec la liste de commandes donnee."""
    return {
        "status": "accepted",
        "language": "en",
        "commands": commands,
        "explanation": "test",
    }


# ------------------------------------------------------------
# Sequences valides
# ------------------------------------------------------------

def test_takeoff_puis_land_est_valide():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "land"},
    ]))

    assert is_valid is True
    assert errors == []


def test_sequence_de_vol_complete_est_valide():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 50, "unit": "cm"},
        {"action": "rotate_clockwise", "value": 90, "unit": "deg"},
        {"action": "land"},
    ]))

    assert is_valid is True
    assert errors == []


def test_requete_telemetrie_seule_est_valide():
    is_valid, errors = validate(accepted([{"action": "query_battery"}]))

    assert is_valid is True
    assert errors == []


# ------------------------------------------------------------
# Coherence de la sequence
# ------------------------------------------------------------

def test_mouvement_sans_takeoff_est_rejete():
    is_valid, errors = validate(accepted([
        {"action": "move_forward", "value": 50},
    ]))

    assert is_valid is False
    assert any("not airborne" in error for error in errors)


def test_double_takeoff_est_rejete():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "takeoff"},
        {"action": "land"},
    ]))

    assert is_valid is False
    assert any("already airborne" in error for error in errors)


def test_commande_apres_land_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "land"},
        {"action": "move_forward", "value": 50},
    ]))

    assert is_valid is False
    assert any("after landing" in error for error in errors)


# ------------------------------------------------------------
# Bornes des valeurs
# ------------------------------------------------------------

def test_distance_trop_grande_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_forward", "value": 9000},
        {"action": "land"},
    ]))

    assert is_valid is False
    assert any("out of range" in error for error in errors)


def test_distance_sous_le_minimum_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_up", "value": 5},
        {"action": "land"},
    ]))

    assert is_valid is False


def test_valeur_manquante_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_forward"},
        {"action": "land"},
    ]))

    assert is_valid is False
    assert any("missing required 'value'" in error for error in errors)


def test_valeur_non_numerique_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_forward", "value": "cinquante"},
        {"action": "land"},
    ]))

    assert is_valid is False
    assert any("must be a number" in error for error in errors)


def test_booleen_nest_pas_accepte_comme_nombre():
    """True vaut 1 en Python : le validateur doit quand meme le refuser."""
    is_valid, _ = validate(accepted([
        {"action": "takeoff"},
        {"action": "move_forward", "value": True},
        {"action": "land"},
    ]))

    assert is_valid is False


# ------------------------------------------------------------
# go_xyz_speed et curve_xyz_speed
# ------------------------------------------------------------

def test_go_xyz_speed_valide():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "go_xyz_speed", "x": 50, "y": 0, "z": 0, "speed": 30},
        {"action": "land"},
    ]))

    assert is_valid is True


def test_go_xyz_speed_tout_a_zero_est_rejete():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "go_xyz_speed", "x": 0, "y": 0, "z": 0, "speed": 30},
        {"action": "land"},
    ]))

    assert is_valid is False
    assert any("cannot all be 0" in error for error in errors)


def test_go_xyz_speed_vitesse_hors_bornes_est_rejetee():
    is_valid, errors = validate(accepted([
        {"action": "takeoff"},
        {"action": "go_xyz_speed", "x": 50, "y": 0, "z": 0, "speed": 500},
        {"action": "land"},
    ]))

    assert is_valid is False


# ------------------------------------------------------------
# Actions inconnues et sorties LLM malformees
# ------------------------------------------------------------

def test_action_inconnue_est_rejetee():
    is_valid, errors = validate(accepted([{"action": "self_destruct"}]))

    assert is_valid is False
    assert any("unknown action" in error for error in errors)


def test_statut_rejected_est_propage():
    is_valid, errors = validate({
        "status": "rejected",
        "language": "unknown",
        "commands": [],
        "explanation": "Only English is supported.",
        "rejection_reason": "Unsupported language.",
    })

    assert is_valid is False
    assert errors == ["Unsupported language."]


def test_accepted_avec_liste_vide_est_rejete():
    is_valid, errors = validate(accepted([]))

    assert is_valid is False


def test_champ_commands_manquant_est_rejete():
    is_valid, errors = validate({"status": "accepted", "language": "en"})

    assert is_valid is False
    assert any("Missing field" in error for error in errors)


def test_entree_non_dict_est_rejetee():
    is_valid, errors = validate("takeoff")

    assert is_valid is False


# ------------------------------------------------------------
# validate_and_report
# ------------------------------------------------------------

def test_rapport_renvoie_les_commandes_si_valide():
    commands = [{"action": "takeoff"}, {"action": "land"}]
    report = validate_and_report(accepted(commands))

    assert report["valid"] is True
    assert report["errors"] == []
    assert report["commands"] == commands


def test_rapport_vide_les_commandes_si_invalide():
    report = validate_and_report(accepted([{"action": "move_forward", "value": 50}]))

    assert report["valid"] is False
    assert report["commands"] == []
    assert len(report["errors"]) > 0
