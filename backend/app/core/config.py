"""
========================================
CONFIGURACIÓN CENTRALIZADA DEL PROYECTO
========================================
Este archivo contiene todos los settings centralizados para el sistema RAG.
Maneja configuración de:
- Rutas de almacenamiento (ChromaDB, PDFs subidos)
- Modelos de embeddings
- Parámetros de chunking
- Configuración del LLM
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración centralizada usando Pydantic Settings.
    Las variables de entorno tienen prioridad sobre los valores por defecto.
    """
    
    # ========== RUTAS ==========
    # Directorio raíz del proyecto (backend/)
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.resolve()
    
    # Directorio del backend (backend/app/)
    BACKEND_ROOT: Path = Path(__file__).parent.parent.resolve()
    
    # Directorio donde se almacenará la base de datos vectorial (chroma_db/)
    CHROMA_DB_PATH: Path = PROJECT_ROOT / "chroma_db"
    
    # Directorio temporal para PDFs subidos (uploaded_pdfs/)
    UPLOAD_DIR: Path = PROJECT_ROOT / "uploaded_pdfs"
    
    # ========== MODELO DE EMBEDDINGS ==========
    # Modelo de HuggingFace para crear embeddings vectoriales
    # "sentence-transformers/all-MiniLM-L6-v2" es rápido y efectivo (~384 dimensiones)
    # alternativa: "sentence-transformers/all-mpnet-base-v2" (más preciso pero más lento)
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # ========== PARÁMETROS DE CHUNKING ==========
    """
    CHUNKING (División de texto en fragmentos):
    El RecursiveCharacterTextSplitter intenta dividir el texto manteniendo
    coherencia semántica. Primero intenta separar por párrafos, luego por
    oraciones, y finalmente por caracteres.
    
    chunk_size: Tamaño máximo de cada fragmento en caracteres
    chunk_overlap: Superposición entre chunks (mantiene contexto entre fragmentos)
    """
    CHUNK_SIZE: int = 1000        # Caracteres por chunk
    CHUNK_OVERLAP: int = 200      # Caracteres de superposición
    
    # Separadores usados en orden de prioridad (el splitter intenta en este orden)
    CHUNK_SEPARATORS: list[str] = ["\n\n", "\n", " ", ""]
    
    # ========== BÚSQUEDA VECTORIAL ==========
    """
    PARÁMETROS DE BÚSQUEDA EN LA BASE VECTORIAL:
    
    k: Número de fragmentos más similares a recuperar
    El valor óptimo depende del tamaño del documento y la complejidad de las preguntas.
    Para PDFs medianos, 4-6 fragmentos suelen ser suficientes.
    """
    TOP_K_RESULTS: int = 5
    
    # Umbral de similitud mínima (0-1). Si es muy bajo, filtra resultados no relevantes.
    SIMILARITY_THRESHOLD: Optional[float] = 0.3
    
    # ========== CONFIGURACIÓN DEL LLM ==========
    """
    El sistema puede usar:
    1. OpenAI GPT (requiere API key en variable OPENAI_API_KEY)
    2. Ollama (ejecuta localmente, más privado, sin costo)
    
    Por defecto configuramos para usar Ollama local.
    """
    
    # Proveedor de LLM: "openai" o "ollama"
    LLM_PROVIDER: str = "ollama"
    
    # Modelo de Ollama (debe estar instalado previamente)
    # Modelos disponibles: llama2, mistral, codellama, etc.
    OLLAMA_MODEL: str = "llama2"
    
    # URL de Ollama (default: localhost:11434)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Timeout para Ollama (en segundos) - aumentar si el modelo es lento
    OLLAMA_TIMEOUT: int = 300  # 5 minutos
    
    # Número de reintentos para Ollama
    OLLAMA_MAX_RETRIES: int = 3
    
    # Modelo de OpenAI (si se usa OpenAI)
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # ========== MEMORIA DEL CHAT ==========
    """
    Configuración para mantener historial de conversación.
    """
    MAX_HISTORY_MESSAGES: int = 10  # Cantidad de intercambios previos a mantener
    
    # ========== METADATA DEL SISTEMA ==========
    APP_NAME: str = "RAG PDF Chat API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        # Permite cargar variables de entorno
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        # Convertir strings a Paths automáticamente
        arbitrary_types_allowed = True


# ========================================
# INSTANCIA GLOBAL DE CONFIGURACIÓN
# ========================================
# Esta instancia se importa en todo el proyecto para acceder a la configuración
settings = Settings()

# Crear directorios necesarios al iniciar
def init_directories():
    """Inicializa los directorios requeridos por la aplicación."""
    settings.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Directorios inicializados:")
    print(f"   - ChromaDB: {settings.CHROMA_DB_PATH}")
    print(f"   - Uploads:  {settings.UPLOAD_DIR}")