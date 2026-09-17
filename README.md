# Tello AI Web Interface

Interface web permettant de piloter un drone DJI Tello à partir de commandes
en langage naturel (anglais). Les instructions de l'utilisateur sont traduites
en séquences de commandes structurées par un LLM (Google Gemini), validées par
un validateur déterministe, converties en code Python `djitellopy`, puis
exécutées sur le drone.

## Architecture

```
Commande utilisateur (anglais)
        │
        ▼
  llm_translator.py     Traduction en JSON structuré (Gemini)
        │
        ▼
 command_validator.py   Validation déterministe (actions, bornes, séquence)
        │
        ▼
   pipeline.py          Application des contraintes du mode d'exécution
        │
        ▼
 code_generator.py      Génération du code Python + exécution djitellopy
        │
        ▼
   Drone DJI Tello
```

Le backend est une API FastAPI ; le frontend est une application React (Vite)
qui consomme cette API.

```
backend/
  main.py                    Point d'entrée FastAPI, CORS, montage du routeur
  api/routes.py              Endpoints HTTP
  core/
    llm_translator.py        Appel Gemini + normalisation de la réponse
    command_validator.py     Validation des commandes et de la séquence
    code_generator.py        Génération de code et exécution réelle
    mock_tello.py            Exécution simulée (sans drone)
    pipeline.py              Orchestration et règles de sécurité par mode
    tello_camera_stream.py   Flux vidéo MJPEG
  utils/tello_manager.py     Singleton de connexion au drone
frontend/                    Application React + Vite
tests/                       Tests unitaires (sans clé API ni drone)
scripts/                     Évaluation du traducteur LLM (appelle Gemini)
```

## Prérequis

- Python 3.11+
- Node.js 18+
- Une clé API Google Gemini (https://aistudio.google.com/apikey)
- Un drone DJI Tello (optionnel : voir le mode `mock`)

## Installation

### Backend

Depuis la racine du projet :

```bash
python -m venv tello-env

# Windows
tello-env\Scripts\activate
# Linux / macOS
source tello-env/bin/activate

pip install -r backend/requirements.txt
```

Créer ensuite un fichier `.env` **à la racine du projet** (même niveau que
`backend/` et `frontend/`), en s'inspirant de `.env.example` :

```bash
cp .env.example .env
```

Puis renseigner la clé :

```
GEMINI_API_KEY=votre_cle_ici
GEMINI_MODEL=gemini-2.5-flash-lite
```

`GEMINI_MODEL` est facultatif ; en son absence, `gemini-2.5-flash-lite` est
utilisé par défaut.

### Frontend

```bash
cd frontend
npm install
```

## Lancement

### 1. Backend

Depuis la racine du projet, avec l'environnement virtuel activé :

```bash
uvicorn backend.main:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000`.
Documentation interactive : `http://127.0.0.1:8000/docs`.

### 2. Frontend

Dans un second terminal :

```bash
cd frontend
npm run dev
```

L'interface est disponible sur `http://localhost:5173`.

### 3. Connexion au drone

Pour toute exécution réelle, l'ordinateur doit être connecté au réseau Wi-Fi
émis par le Tello (`TELLO-XXXXXX`) **avant** l'envoi d'une commande. Le drone
doit être allumé et disposer d'au moins 20 % de batterie : en dessous,
l'exécution est refusée par `code_generator.py`.

## Modes d'exécution

L'API accepte quatre modes via le champ `execution_mode` :

| Mode | Comportement |
|------|--------------|
| `mock` | Simulation complète, aucun drone requis |
| `real_first_flight` | Drone réel, vol bridé |

Le mode `real_first_flight` n'autorise que `takeoff`, `land`, la lecture de
batterie, les déplacements sur les six axes et les rotations. Les flips,
l'arrêt d'urgence et le vol en coordonnées (`go_xyz_speed`, `curve_xyz_speed`)
sont bloqués. Les déplacements sont plafonnés à 50 cm et les rotations à 90°,
et toute séquence contenant une action de vol doit commencer par `takeoff` et
se terminer par `land`.

**L'interface web utilise exclusivement `real_first_flight`** (codé en dur dans
`frontend/src/services/telloApi.js`) : aucune commande envoyée depuis l'UI ne
peut produire un vol non borné. Le mode `mock` reste accessible via l'API afin
de pouvoir évaluer le projet sans drone.

## Tests

### Tests unitaires

Reproductibles, sans clé API ni drone :

```bash
pytest tests/
```

44 tests couvrant le validateur de commandes (bornes des valeurs, cohérence des
séquences, sorties LLM malformées), le générateur de code Python, et les règles
de sécurité du mode `real_first_flight`.

### Évaluation du traducteur LLM

```bash
python -m scripts.eval_llm_translator
```

Ce script est délibérément séparé de `tests/` : il appelle réellement l'API
Gemini, nécessite une clé valide, consomme des tokens, et son résultat peut
varier d'une exécution à l'autre puisque la sortie du modèle n'est pas
déterministe. Ce n'est donc pas un test unitaire, mais une évaluation de la
qualité de traduction sur un jeu de scénarios.

## Limites connues

- **Langue** : seul l'anglais est accepté. Toute commande en français, arabe ou
  en langue mixte est rejetée avec `language: "unknown"`.
- **Clé API requise même en mode `mock`** : la simulation ne porte que sur
  l'exécution des commandes ; l'étape de traduction passe toujours par Gemini.
- **Atterrissage de sécurité au mieux** : si une exception survient alors que le
  drone est en vol, un `land()` est tenté et tracé dans les logs. Si cet appel
  échoue lui aussi (perte de liaison Wi-Fi par exemple), le drone reste en vol
  stationnaire jusqu'à l'auto-atterrissage du firmware.
- **Caméra** : `streamon` / `streamoff` ne font pas partie des actions autorisées
  en mode `real_first_flight`. Le flux vidéo se pilote via les endpoints
  `/api/video/*`.
- **Connexion unique** : un seul `TelloManager` (singleton) est partagé entre
  l'exécution des commandes et le flux vidéo, afin d'éviter les conflits de
  ports UDP. `POST /api/video/stop` n'arrête donc que le flux vidéo et laisse
  la connexion ouverte pour les commandes suivantes.
- **Pas d'authentification** : l'API est destinée à un usage local uniquement.
- **CORS** : `allow_origins=["*"]` est configuré pour le développement local
  uniquement.

## Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/pipeline` | Traduit, valide et exécute une commande |
| `GET` | `/api/video/stream` | Flux vidéo MJPEG |
| `POST` | `/api/video/stop` | Arrête le flux vidéo |
| `GET` | `/api/video/status` | État du flux |
| `GET` | `/health` | Vérification de disponibilité |

Exemple :

```bash
curl -X POST http://127.0.0.1:8000/api/pipeline \
  -H "Content-Type: application/json" \
  -d '{"command": "take off then land", "execution_mode": "mock"}'
```
