--- README.md (原始)


+++ README.md (修改后)
# Tello AI Web Interface

A full-stack web application that translates natural-language commands into validated DJI Tello drone actions using Google's Gemini AI.

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core business logic
│   │   ├── llm_translator.py      # Natural language processing
│   │   ├── command_validator.py   # Command validation & safety checks
│   │   ├── code_generator.py      # Python code generation
│   │   ├── mock_tello.py          # Mock drone for testing
│   │   ├── pipeline.py            # Main execution pipeline
│   │   └── tello_camera_stream.py # Camera streaming
│   ├── main.py             # FastAPI application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Application pages
│   │   ├── context/        # React context providers
│   │   └── services/       # API services
│   └── package.json
└── tests/                  # Test suite
```

## Features

- **Natural Language Processing**: Convert English commands to structured drone actions
- **Safety Validation**: Multi-layer validation including:
  - Sequence validation (takeoff before movement, land at end)
  - Range validation (distance, speed, angle limits)
  - Execution mode safety levels
- **Multiple Execution Modes**:
  - `mock`: Safe simulation without hardware
  - `real_first_flight`: Restricted safe mode for beginners
  - `real_safe`: Only passive telemetry queries
  - `real`: Full drone control
- **Code Generation**: Automatic DJITelloPy code generation
- **Real-time Monitoring**: Camera stream and telemetry display

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Google Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

5. Start the backend server:
```bash
cd /workspace
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at: http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure the API URL (optional, default: http://127.0.0.1:8000):

   Edit `src/services/telloApi.js` if you need to change the backend URL.

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

## Usage Examples

### Natural Language Commands

The system understands various English phrasings:

**Takeoff and Movement:**
- "Take off and move forward 50 cm"
- "Launch the drone then fly straight"
- "Lift off and go ahead"

**Rotation:**
- "Turn right 90 degrees"
- "Rotate clockwise"
- "Spin left"

**Queries:**
- "Check battery level"
- "What's the current height?"
- "Show me the temperature"

**Camera:**
- "Start camera"
- "Turn on video stream"

### Safety Features

The system includes multiple safety layers:

1. **Language Validation**: Only English commands are accepted
2. **Ambiguity Detection**: Vague commands like "fly around" are rejected
3. **Sequence Validation**: Ensures proper takeoff → actions → land sequence
4. **Range Validation**: Enforces safe distance, speed, and angle limits
5. **Execution Modes**: Progressive safety levels from mock to real flight

### Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `mock` | Software simulation only | Development & testing |
| `real_first_flight` | Restricted movements (< 30cm, < 45°) | First-time pilots |
| `real_safe` | Passive queries only | Monitoring without flight |
| `real` | Full drone control | Experienced pilots |

## API Endpoints

### POST `/api/pipeline`
Execute a natural language command through the full pipeline.

**Request:**
```json
{
  "command": "take off and move forward 50 cm",
  "execution_mode": "mock"
}
```

**Response:**
```json
{
  "success": true,
  "execution_mode": "mock",
  "llm_output": {
    "status": "accepted",
    "language": "en",
    "commands": [
      {"action": "takeoff"},
      {"action": "move_forward", "value": 50, "unit": "cm"}
    ],
    "explanation": "Command interpreted successfully"
  },
  "validation": {
    "valid": true,
    "errors": [],
    "commands": [...]
  },
  "generated_code": "from djitellopy import Tello\n...",
  "execution": {...},
  "error": null
}
```

### GET `/api/video/stream`
Stream camera feed from the drone (MJPEG format).

### POST `/api/video/stop`
Stop the camera stream.

### GET `/api/video/status`
Get camera stream status.

### GET `/health`
Health check endpoint.

## Testing

### Backend Tests

Run the LLM translator tests:
```bash
cd /workspace
python tests/test_llm_translator.py
```

### Manual Testing with Mock Mode

Test the pipeline without API calls:
```python
import sys
sys.path.insert(0, '.')
from backend.core.mock_tello import execute_commands

commands = [
    {'action': 'takeoff'},
    {'action': 'move_forward', 'value': 50},
    {'action': 'rotate_clockwise', 'value': 90},
    {'action': 'land'}
]

result = execute_commands(commands)
print(result)
```

## Architecture

### Pipeline Flow

1. **User Input** → Natural language command
2. **LLM Translation** → Structured JSON commands (Google Gemini)
3. **Validation** → Safety and sequence checks
4. **Code Generation** → DJITelloPy Python code
5. **Execution** → Mock or real drone execution
6. **Response** → Results, logs, and telemetry

### Security Considerations

- API keys stored in `.env` file (not committed to version control)
- CORS configured for local development (update for production)
- Input validation at multiple levels
- Emergency stop functionality available

## Troubleshooting

### Common Issues

**"LLM API key is missing"**
- Ensure `.env` file exists in the project root
- Verify `GEMINI_API_KEY` is set correctly

**"ModuleNotFoundError: No module named 'backend'"**
- Run Python commands from the project root (`/workspace`)
- Or add the project root to PYTHONPATH

**Frontend cannot connect to backend**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API URL in `frontend/src/services/telloApi.js`

**Drone connection errors**
- Ensure drone is powered on and connected to WiFi
- Check battery level (> 20% required)
- Verify network connectivity

## Requirements

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- google-genai
- djitellopy
- opencv-python
- python-dotenv

### Frontend
- Node.js 18+
- React 18+
- Vite
- Material-UI (MUI)
- React Router

## License

This project is for educational purposes (TP submission).

## Author

Student Project - Tello AI Web Interface

## Support

For issues or questions, please refer to the documentation or contact the project author.
