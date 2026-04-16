# 🤖 Chat con tus Documentos PDF

**Asistente virtual para buscar y chatear sobre tus documentos de RRHH**

---

## ¿Qué hace esta aplicación?

Imaginate tener un asistente que **lee todos tus PDFs de políticas, beneficios, procedimientos** y puede responder preguntas como:

- "¿Cuáles son los días de licencia por paternidad?"
- "¿Cuántos días de vacaciones me corresponden según mi antigüedad?"
- "¿Cuál es el plazo para presentar los comprobantes de gasto?"

**¡Eso exactamente hace esta app!**

Subís un documento PDF y después le ponés preguntas en lenguaje natural. El sistema busca la información relevante y te la explica con tus propias palabras.

---

## ¿Para quién es?

Para vos, si trabajás en:
- Recursos Humanos
- Administración de Personal
- Legales
- Cualquier área que maneje muchos documentos

Necesás **saber usar una computadora a nivel básico** y tener acceso al sistema de tu empresa.

---

## ¿Cómo la uso?

### Paso 1: Iniciá el sistema

**Si ya está instalado** (preguntá a Sistemas), simplemente ejecutá:

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

Después abrí en tu navegador: **http://localhost:3000**

### Paso 2: Subir un PDF

1. **Arrastrá** un archivo PDF al área indicated (o hacé clic para buscarlo)
2. **Esperá** a que termine de "indexar" (puede tomar unos segundos, según el tamaño)
3. Vas a ver el documento aparecer en la lista de la izquierda

### Paso 3: Hacer preguntas

1. **Hacé clic** en el documento que querés consultar (se va a marcar como seleccionado)
2. **Escribí** tu pregunta en el chat
3. ¡Listo! El sistema te responde

---

## Ejemplos de preguntas que podés hacer

| Si tu PDF es de... | Podés preguntar... |
|---|---|
| Políticas de RRHH | "¿Cuál es la política de licencias por enfermedad?" |
| Liquidaciones | "¿Cómo se calcula el adicional por presentismo?" |
| Convenios colectivos | "¿Cuáles son los adicionales por turno noche?" |
| Procedimientos | "¿Cuál es el plazo para resolver un reclamo?" |
| Beneficios | "¿Qué cubre el plan de medicina prepaga?" |
| Manual de empleados | "¿Qué debo hacer si me enfero?" |

---

## Funcionalidades útiles

### 📂 Múltiples documentos
Podés subir **hasta 3 PDFs a la vez**. Cada uno se procesa por separado y queda en la lista.

### 🔍 Buscar en un documento específico
Cuando hacés **clic** en un documento de la lista, el chat busca **solo en ese PDF**.

Si no hacés clic en ninguno, el chat busca en **todos los documentos** que hayas subido.

### 👁️ El visualizador
Abajo del todo podés ver el PDF que estás consultando. Es útil para verificar la fuente de la información.

### 🗑️ Eliminar documentos
Si necesitás sacar un documento del sistema, hacé clic en el ícono de papelera en la tarjeta del documento.

---

## ¿Qué pasa si no responde bien?

Si el sistema te dá una respuesta que no tiene sentido o dice que "no encontró información":

1. **Revisá que hayas seleccionado el documento correcto** (haciendo clic en él)
2. **Probá con otras palabras** - a veces conviene reformular la pregunta
3. **Verificá que el PDF tenga texto** (no es una imagen escaneada)

Si el error persiste, comunicate con el área de Sistemas.

---

# 📋 Guía Técnica (para Developers)

## Estructura del Proyecto

```
pdf-rag-chat/
├── backend/                    # API REST con FastAPI
│   ├── app/
│   │   ├── core/config.py      # Configuración
│   │   ├── models/schemas.py # Schemas Pydantic
│   │   ├── services/
│   │   │   ├── pdf_processor.py # Extracción de PDFs
│   │   │   └── rag_service.py  # Pipeline RAG
│   │   └── main.py            # Endpoints
│   └── requirements.txt
│
├── frontend/                   # Interfaz React
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx    # Upload y lista de docs
│   │   │   └── ChatWindow.jsx # Chat UI
│   │   ├── services/api.js    # Cliente API
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)
- **Ollama** (LLM local) - o usar OpenAI

### Backend

```bash
cd backend

# Crear entorno virtual
py -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar Ollama (si usás LLM local)
ollama serve
ollama pull llama2  # o mistral, codellama, etc.

# Arrancar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## ⚙️ Configuración

### Variables de Entorno

**Backend** (`backend/.env`):
```env
# OpenAI (opcional)
OPENAI_API_KEY=sk-tu-api-key
LLM_PROVIDER=openai

# O Ollama (por defecto)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
```

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificar estado del servidor |
| POST | `/upload` | Subir y indexar un PDF |
| POST | `/query` | Consultar sobre el documento |
| GET | `/documents` | Lista de documentos |
| DELETE | `/documents/{name}` | Eliminar documento |
| GET | `/file/{name}` | Ver archivo PDF |
| GET | `/stats` | Estadísticas del sistema |
| POST | `/reset` | Limpiar historial |

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web
- **LangChain** - Orquestación de LLMs
- **ChromaDB** - Base de datos vectorial
- **Ollama** - LLM local
- **HuggingFace** - Embeddings

### Frontend
- **React 18** - UI
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **Axios** - Cliente HTTP

---

## 📝 Licencia

MIT License - Libremente modificable y distribuible.

---

##Versión

1.0.0 - Abril 2026