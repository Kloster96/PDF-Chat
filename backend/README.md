# 📄 Backend - RAG PDF Chat API

API REST para el sistema de chat con PDFs usando FastAPI, ChromaDB y LangChain.

## 🚀 Instalación

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
py -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

### 1. Iniciar Ollama (LLM local)

```bash
ollama serve
ollama pull llama2
```

### 2. Iniciar FastAPI

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload` | Subir PDF |
| POST | `/query` | Consultar documento |
| GET | `/stats` | Estadísticas |
| POST | `/reset` | Limpiar conversación |

## 🔧 Configuración

Editar `app/core/config.py`:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `EMBEDDINGS_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Modelo de embeddings |
| `CHUNK_SIZE` | `1000` | Tamaño de chunk |
| `CHUNK_OVERLAP` | `200` | Superposición |
| `LLM_PROVIDER` | `ollama` | `ollama` o `openai` |
| `OLLAMA_MODEL` | `llama2` | Modelo Ollama |

## 📁 Estructura

```
backend/
├── app/
│   ├── core/           # Configuración
│   │   └── config.py
│   ├── models/        # Schemas Pydantic
│   │   └── schemas.py
│   ├── services/      # Lógica de negocio
│   │   ├── pdf_processor.py
│   │   └── rag_service.py
│   └── main.py        # Endpoints
├── requirements.txt
└── README.md
```

## 🛠️ Tecnologías

- FastAPI, LangChain, ChromaDB, Ollama, HuggingFace