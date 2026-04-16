"""
========================================
MAIN.PY - PUNTO DE ENTRADA DE LA API
========================================
Este archivo define los endpoints de FastAPI y orquesta las solicitudes.

ENDPOINTS DISPONIBLES:
- POST /upload: Cargar un archivo PDF
- POST /query: Consultar sobre el contenido
- GET /stats: Ver estadísticas del sistema
- POST /reset: Limpiar historial de conversación
- GET /health: Health check
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Importar configuración
from app.core.config import settings, init_directories

# Importar modelos Pydantic
from app.models.schemas import (
    UploadResponse,
    QueryRequest,
    QueryResponse,
    StatsResponse,
    HealthResponse,
    ErrorResponse
)

# Importar servicio RAG
from app.services.rag_service import rag_service


# ========================================
# INICIALIZACIÓN DE LA APP
# ========================================

# Configurar logging
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)

# Crear app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Sistema RAG para Chat con PDFs
    
    Este API permite:
    - **Subir PDFs** y indexarlos en una base de datos vectorial (ChromaDB)
    - **Consultar** el contenido usando búsqueda vectorial y un LLM
    - **Mantener contexto** de la conversación
    
    ### Flujo de trabajo:
    1. Enviar un PDF al endpoint `/upload`
    2. El sistema extrae el texto, lo fragmenta en chunks y lo indexa
    3. Enviar preguntas al endpoint `/query`
    4. El sistema busca contexto relevante y genera respuestas
    
    ### Tecnologías:
    - FastAPI (backend)
    - LangChain (orquestación)
    - ChromaDB (base vectorial)
    - Ollama (LLM local)
    - HuggingFace Embeddings
    """,
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc"         # ReDoc alternative
)

# Configurar CORS para permitir conexiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplazar con dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# ENDPOINTS
# ========================================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar la aplicación."""
    # Inicializar directorios
    init_directories()
    
    logger.info(f"🚀 {settings.APP_NAME} iniciado")
    logger.info(f"   📂 ChromaDB: {settings.CHROMA_DB_PATH}")
    logger.info(f"   🔢 Embeddings: {settings.EMBEDDINGS_MODEL}")
    logger.info(f"   🤖 LLM: {settings.LLM_PROVIDER}/{settings.OLLAMA_MODEL}")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información básica."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "stats": "/stats",
            "reset": "/reset",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Útil para verificar que el servicio está corriendo.
    """
    return HealthResponse(
        status="healthy",
        message=f"{settings.APP_NAME} funcionando correctamente"
    )


@app.post(
    "/upload", 
    response_model=UploadResponse,
    tags=["Documents"],
    summary="Subir PDF",
    description="""
    ## Upload de PDF
    
    Este endpoint recibe un archivo PDF, lo procesa y lo indexa en ChromaDB.
    
    **Proceso:**
    1. Recibe el archivo PDF
    2. Extrae el texto usando pypdf
    3. Divide el texto en chunks (fragmentos)
    4. Convierte cada chunk a vector (embeddings)
    5. Guarda los vectores en ChromaDB
    6. Guarda el archivo para poder visualizarlo después
    
    **Parametros:**
    - file: Archivo PDF (multipart/form-data)
    
    **Returns:**
    - chunks_count: Cantidad de chunks creados
    - total_documents: Total en la base vectorial
    """
)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Carga un archivo PDF y lo indexa en la base de datos vectorial.
    
    El archivo se guarda temporalmente, se procesa, y luego se elimina.
    """
    # Validar que sea PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF"
        )
    
    logger.info(f"📄 Recibido archivo: {file.filename}")
    
    # Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=".pdf",
        dir=str(settings.UPLOAD_DIR)
    ) as tmp_file:
        # Leer contenido del archivo
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Procesar y indexar el PDF
        result = rag_service.add_documents(tmp_path, file.filename)
        
        logger.info(f"✅ PDF indexado: {result['chunks_count']} chunks")
        
        # Mover el archivo a la carpeta de uploads (no borrar)
        import shutil
        final_path = settings.UPLOAD_DIR / file.filename
        shutil.move(tmp_path, final_path)
        
        return UploadResponse(
            status="success",
            chunks_count=result["chunks_count"],
            total_documents=result["total_documents"],
            message=result["message"],
            filename=file.filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error procesando PDF: {str(e)}")
        # Limpiar archivo en caso de error
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el PDF: {str(e)}"
        )


@app.get(
    "/files/{filename}", 
    tags=["Files"],
    summary="Obtener archivo PDF",
    description="Retorna un archivo PDF previamente subido."
)
async def get_file(filename: str):
    """Serve the uploaded PDF file."""
    file_path = settings.UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )


@app.post(
    "/query", 
    response_model=QueryResponse,
    tags=["Chat"],
    summary="Consultar PDF",
    description="""
    ## Consulta al sistema RAG
    
    Este endpoint recibe una pregunta y retorna la respuesta generada por el LLM.
    
    **Proceso:**
    1. Convierte la pregunta a vector (embeddings)
    2. Busca los k documentos más similares en ChromaDB (retrieval)
    3. Construye un prompt con el contexto recuperado
    4. Envía el prompt al LLM (generation)
    5. Retorna la respuesta
    
    **Parámetros:**
    - question: Pregunta del usuario (JSON body)
    
    **Returns:**
    - answer: Respuesta del LLM
    - sources: Documentos fuente utilizados
    - conversation_history: Historial de la conversación
    """
)
async def query_pdf(request: QueryRequest):
    """
    Consulta el contenido del PDF indexado.
    
    Mantiene historial de conversación para contexto.
    """
    logger.info(f"💬 Consulta recibida: {request.question}")
    if request.document_name:
        logger.info(f"   📄 Documento específico: {request.document_name}")
    
    try:
        # Ejecutar pipeline RAG
        result = rag_service.query(request.question, request.document_name)
        
        logger.info(f"✅ Respuesta generada ({len(result['answer'])} caracteres)")
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_history=result["conversation_history"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error en consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la consulta: {str(e)}"
        )


@app.get(
    "/stats", 
    response_model=StatsResponse,
    tags=["System"],
    summary="Estadísticas",
    description="Retorna estadísticas de la base de datos vectorial y configuración del sistema."
)
async def get_stats():
    """Obtiene estadísticas del sistema RAG."""
    try:
        stats = rag_service.get_stats()
        
        return StatsResponse(
            total_documents=stats["total_documents"],
            embedding_model=stats["embedding_model"],
            llm_provider=stats["llm_provider"],
            llm_model=stats["llm_model"],
            chunk_size=stats["chunk_size"],
            chunk_overlap=stats["chunk_overlap"],
            top_k=stats["top_k"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@app.post(
    "/reset", 
    tags=["System"],
    summary="Resetear conversación",
    description="Limpia el historial de conversación."
)
async def reset_conversation():
    """Limpia el historial de conversación."""
    try:
        rag_service.reset_conversation()
        
        return {
            "status": "success",
            "message": "Historial de conversación limpiado"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en reset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar historial: {str(e)}"
        )


@app.get(
    "/documents", 
    tags=["Documents"],
    summary="Listar documentos",
    description="Retorna la lista de documentos indexados."
)
async def get_documents():
    """Obtiene la lista de documentos indexados."""
    try:
        documents = rag_service.get_documents_list()
        
        return {
            "status": "success",
            "documents": documents,
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener documentos: {str(e)}"
        )


@app.delete(
    "/documents/{document_name}", 
    tags=["Documents"],
    summary="Eliminar documento",
    description="Elimina un documento específico de la base vectorial."
)
async def delete_document(document_name: str):
    """Elimina un documento por nombre."""
    try:
        result = rag_service.delete_document(document_name)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar documento: {str(e)}"
        )


@app.delete(
    "/documents", 
    tags=["Documents"],
    summary="Eliminar todos los documentos",
    description="Elimina todos los documentos de la base vectorial."
)
async def clear_all_documents():
    """Elimina todos los documentos."""
    try:
        result = rag_service.clear_all_documents()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error limpiando documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar documentos: {str(e)}"
        )


# ========================================
# MANEJO DE ERRORES
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Manejo personalizado de HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Manejo de errores generales."""
    logger.error(f"💥 Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc)
        }
    )


# ========================================
# PUNTO DE ENTRADA
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )