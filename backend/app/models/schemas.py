"""
========================================
SCHEMAS PYDANTIC - MODELOS DE DATOS
========================================
Define los modelos de datos para validación de requests y responses.
Usamos Pydantic para:
- Validación automática de datos de entrada
- Documentación automática en Swagger UI
- Tipado fuerte en toda la aplicación
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ========================================
# SCHEMAS PARA UPLOAD
# ========================================

class UploadResponse(BaseModel):
    """Response del endpoint de upload."""
    status: str = Field(..., description="Estado de la operación")
    chunks_count: int = Field(..., description="Cantidad de chunks creados")
    total_documents: int = Field(..., description="Total de documentos en la base")
    message: str = Field(..., description="Mensaje descriptivo")
    filename: Optional[str] = Field(None, description="Nombre del archivo cargado")


# ========================================
# SCHEMAS PARA CONSULTA
# ========================================

class SourceDocument(BaseModel):
    """Documento fuente recuperado de la búsqueda vectorial."""
    content: str = Field(..., description="Contenido del chunk (truncado)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata del documento")


class QueryRequest(BaseModel):
    """Request para el endpoint de consulta."""
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="Pregunta del usuario sobre el contenido del PDF"
    )
    document_name: Optional[str] = Field(
        None,
        description="Nombre específico del documento a consultar (opcional)"
    )


class QueryResponse(BaseModel):
    """Response del endpoint de consulta."""
    answer: str = Field(..., description="Respuesta generada por el LLM")
    sources: List[SourceDocument] = Field(
        default_factory=list, 
        description="Documentos fuente usados para generar la respuesta"
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Historial de la conversación"
    )


# ========================================
# SCHEMAS PARA ESTADÍSTICAS
# ========================================

class StatsResponse(BaseModel):
    """Response con estadísticas del sistema."""
    total_documents: int = Field(..., description="Cantidad de documentos indexados")
    embedding_model: str = Field(..., description="Modelo de embeddings usado")
    llm_provider: str = Field(..., description="Proveedor del LLM (openai/ollama)")
    llm_model: str = Field(..., description="Modelo del LLM")
    chunk_size: int = Field(..., description="Tamaño de chunk configurado")
    chunk_overlap: int = Field(..., description="Superposición de chunks")
    top_k: int = Field(..., description="Cantidad de resultados en búsqueda")


# ========================================
# SCHEMAS GENERALES
# ========================================

class HealthResponse(BaseModel):
    """Response para health check."""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Response para errores."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)