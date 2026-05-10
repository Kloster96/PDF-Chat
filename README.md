# 🤖 Chat with your PDF Documents

**AI assistant to search and chat with your HR documents**

---

## What does this app do?

Imagine having an assistant that **reads all your PDFs** (policies, benefits, procedures) and can answer questions like:

- "What are the paternity leave days?"
- "How many vacation days do I get based on my seniority?"
- "What's the deadline to submit expense receipts?"

**That's exactly what this app does!**

Upload a PDF document and then ask questions in natural language. The system finds the relevant information and explains it to you.

---

## Who is this for?

For anyone working in:
- Human Resources
- Personnel Administration
- Legal
- Any department that handles lots of documents

You just need **basic computer skills** and access to your company's system.

---

## How do I use it?

### Step 1: Start the system

**If already installed** (ask IT), just run:

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

Then open in your browser: **http://localhost:3000**

### Step 2: Upload a PDF

1. **Drag** a PDF file to the indicated area (or click to browse)
2. **Wait** for it to finish "indexing" (may take a few seconds depending on size)
3. You'll see the document appear in the list on the left

### Step 3: Ask questions

1. **Click** on the document you want to query (it will be marked as selected)
2. **Type** your question in the chat
3. Done! The system answers you

---

## Example questions you can ask

| If your PDF is about... | You can ask... |
|---|---|
| HR Policies | "What is the sick leave policy?" |
| Payroll | "How is the attendance bonus calculated?" |
| Collective agreements | "What are the night shift allowances?" |
| Procedures | "What's the deadline to resolve a complaint?" |
| Benefits | "What does the health insurance plan cover?" |
| Employee handbook | "What should I do if I get sick?" |

---

## Useful Features

### 📂 Multiple documents
You can upload **up to 3 PDFs at once**. Each one is processed separately and stays in the list.

### 🔍 Search in a specific document
When you **click** on a document in the list, the chat searches **only in that PDF**.

If you don't click on any, the chat searches in **all uploaded documents**.

### 👁️ The viewer
At the bottom you can view the PDF you're consulting. Useful for verifying the source of information.

### 🗑️ Delete documents
If you need to remove a document from the system, click the trash icon on the document card.

---

## What if it doesn't respond well?

If the system gives you an answer that doesn't make sense or says "no information found":

1. **Check that you've selected the correct document** (by clicking on it)
2. **Try different wording** - sometimes rephrasing the question helps
3. **Verify that the PDF contains text** (not a scanned image)

If the error persists, contact IT.

---

# 📋 Technical Guide (for Developers)

## Project Structure

```
pdf-rag-chat/
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── core/config.py      # Configuration
│   │   ├── models/schemas.py  # Pydantic schemas
│   │   ├── services/
│   │   │   ├── pdf_processor.py # PDF extraction
│   │   │   └── rag_service.py  # RAG pipeline
│   │   └── main.py            # Endpoints
│   └── requirements.txt
│
├── frontend/                   # React UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx    # Upload and doc list
│   │   │   └── ChatWindow.jsx # Chat UI
│   │   ├── services/api.js    # API client
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)
- **Ollama** (local LLM) - or use OpenAI

### Backend

```bash
cd backend

# Create virtual environment
py -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Ollama (if using local LLM)
ollama serve
ollama pull llama2  # or mistral, codellama, etc.

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## ⚙️ Configuration

### Environment Variables

**Backend** (`backend/.env`):
```env
# OpenAI (optional)
OPENAI_API_KEY=sk-your-api-key
LLM_PROVIDER=openai

# Or Ollama (default)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check server status |
| POST | `/upload` | Upload and index a PDF |
| POST | `/query` | Query the document |
| GET | `/documents` | List documents |
| DELETE | `/documents/{name}` | Delete document |
| GET | `/file/{name}` | View PDF file |
| GET | `/stats` | System statistics |
| POST | `/reset` | Clear conversation history |

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Web framework
- **LangChain** - LLM orchestration
- **ChromaDB** - Vector database
- **Ollama** - Local LLM
- **HuggingFace** - Embeddings

### Frontend
- **React 18** - UI
- **Vite** - Build tool
- **Tailwind CSS** - Styles
- **Axios** - HTTP client

---

## 📝 License

MIT License - Freely modifiable and distributable.

---

## Version

1.0.0 - April 2026