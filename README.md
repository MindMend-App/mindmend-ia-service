# MindMend IA Service

Micro-servicio FastAPI que expone dos endpoints:

- `POST /chat`  
  - **Request** `{ "message": "Hola, ¿cómo estás?" }`  
  - **Response** `{ "reply": "¡Hola! Estoy aquí para escucharte." }`

- `POST /analyze`  
  - **Request** `{ "messages": ["Me siento nervioso", "No duermo"] }`  
  - **Response** `{ "label": "fear", "score": 0.92 }`

## Arranque

1. Crear y activar entorno virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate # macOS/Linux

