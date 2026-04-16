"""
========================================
SERVICIO RAG - CORE DEL SISTEMA
========================================
Este módulo implementa el pipeline completo de Retrieval-Augmented Generation:

1. INDEXING (Carga de documentos):
   - Recibe chunks de texto
   - Los convierte a vectores usando embeddings
   - Los almacena en ChromaDB (base vectorial)

2. RETRIEVAL (Búsqueda):
   - Recibe la pregunta del usuario
   - La convierte a vector usando mismos embeddings
   - Busca los k chunks más similares (búsqueda vectorial)

3. GENERATION (Generación de respuesta):
   - Arma el prompt con contexto + pregunta
   - Envía al LLM (Ollama o OpenAI)
   - Retorna la respuesta

¿CÓMO FUNCIONA LA BÚSQUEDA VECTORIAL?
--------------------------------------
Cada chunk de texto se convierte en un vector numérico (embedding) de ~384 dimensiones.
Cuando el usuario hace una pregunta, también se convierte a vector.
La "similitud" se calcula usando cosine similarity:
- Vectores similares = respuesta semánticamente relacionada
- ChromaDB usa HNSW (algoritmo de vecindad) para buscar rápido

Esto es mucho mejor que búsqueda por palabras clave porque:
- Entiende el significado, no solo palabras exactas
- "Capital de Francia" y "Paris" son similares aunque no comparten palabras
"""

from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import uuid

# LangChain - Componentes para RAG
from langchain_core.documents import Document  #新版 langchain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.services.pdf_processor import pdf_processor


class RAGService:
    """
    Servicio principal que orquesta todo el pipeline RAG.
    Maneja la base de datos vectorial y las consultas al LLM.
    """
    
    def __init__(self):
        """Inicializa el servicio RAG."""
        self._vector_store: Optional[Chroma] = None
        self._embeddings = None
        self._llm = None
        
        # Historial de conversación (en memoria - para producción usar Redis/DB)
        self.conversation_history: List[Dict[str, str]] = []
        
        # Inicializar embeddings y LLM
        self._init_embeddings()
        self._init_llm()
    
    def _init_embeddings(self):
        """
        Inicializa el modelo de embeddings de HuggingFace.
        
        Los embeddings transforman texto en vectores numéricos.
        Usamos 'all-MiniLM-L6-v2' que:
        - Produce vectores de 384 dimensiones
        - Es rápido y preciso
        - No requiere API key (ejecuta local)
        """
        print(f"🔢 Inicializando embeddings: {settings.EMBEDDINGS_MODEL}")
        
        self._embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDINGS_MODEL,
            model_kwargs={'device': 'cpu'}  # Cambiar a 'cuda' si tenés GPU
        )
        
        print("   ✅ Embeddings inicializados")
    
    def _init_llm(self):
        """
        Inicializa el modelo de lenguaje (LLM).
        
        Soporta Ollama (local) o OpenAI (cloud).
        """
        if settings.LLM_PROVIDER == "ollama":
            print(f"🤖 Configurando Ollama: {settings.OLLAMA_MODEL}")
            self._llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.7,  # Creatividad de las respuestas
                timeout=settings.OLLAMA_TIMEOUT,  # Timeout más largo
                max_retries=settings.OLLAMA_MAX_RETRIES,  # Reintentos
            )
            print(f"   ✅ Ollama conectado (timeout: {settings.OLLAMA_TIMEOUT}s)")
            
        elif settings.LLM_PROVIDER == "openai":
            print(f"🤖 Configurando OpenAI: {settings.OPENAI_MODEL}")
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                timeout=300  # 5 minutos para OpenAI también
            )
            print("   ✅ OpenAI conectado")
    
    @property
    def vector_store(self) -> Chroma:
        """Accede a la base de datos vectorial (lazy initialization)."""
        if self._vector_store is None:
            self._load_or_create_vector_store()
        return self._vector_store
    
    def _load_or_create_vector_store(self):
        """
        Carga la base de datos vectorial existente o crea una nueva.
        
        ChromaDB persiste automáticamente en el directorio configurado.
        """
        print(f"📂 Cargando ChromaDB desde: {settings.CHROMA_DB_PATH}")
        
        # Verificar si existe una base de datos previa
        if os.path.exists(settings.CHROMA_DB_PATH) and any(os.scandir(settings.CHROMA_DB_PATH)):
            # Cargar base existente
            self._vector_store = Chroma(
                persist_directory=str(settings.CHROMA_DB_PATH),
                embedding_function=self._embeddings
            )
            print(f"   ✅ Base existente cargada (docs: {self._vector_store._collection.count()})")
        else:
            # Crear nueva base (se inicializa vacía)
            self._vector_store = Chroma(
                persist_directory=str(settings.CHROMA_DB_PATH),
                embedding_function=self._embeddings
            )
            print("   ✅ Nueva base de datos vectorial creada")
    
    def add_documents(self, pdf_path: str, document_name: str = None) -> Dict[str, Any]:
        """
        Pipeline completo para agregar un PDF al sistema RAG.
        
        Pasos:
        1. Procesar PDF (extraer texto y crear chunks)
        2. Convertir chunks a documentos LangChain
        3. Generar embeddings y guardar en ChromaDB
        
        Args:
            pdf_path: Ruta al archivo PDF
            document_name: Nombre real del documento (opcional)
            
        Returns:
            Dict con información de la carga (cantidad de chunks, etc.)
        """
        # Usar el nombre proporcionado o extraer del path
        if document_name is None:
            document_name = os.path.basename(pdf_path)
        
        print(f"\n📥 Agregando documento: {document_name}")
        
        # Paso 1: Procesar PDF (extraer y chunkear)
        chunks = pdf_processor.process_pdf(pdf_path)
        
        if not chunks:
            raise ValueError("No se pudo extraer texto del PDF")
        
        # Paso 2: Crear documentos LangChain
        # Cada documento tiene content + metadata (para tracking)
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "source": document_name,
                    "chunk_index": i,
                    "timestamp": datetime.now().isoformat()
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        print(f"📝 Creando {len(documents)} documentos para indexing...")
        
        # Paso 3: Indexar en ChromaDB
        # Esto convierte cada chunk a vector y lo guarda
        if self._vector_store is None:
            # Primera vez - crear nueva colección
            self._vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self._embeddings,
                persist_directory=str(settings.CHROMA_DB_PATH)
            )
            print(f"   ✅ Primera indexación completada")
        else:
            # Agregar a colección existente
            self._vector_store.add_documents(documents)
            print(f"   ✅ Documentos agregados a la colección existente")
        
        # Persistir cambios
        self._vector_store.persist()
        
        return {
            "status": "success",
            "chunks_count": len(chunks),
            "total_documents": self._vector_store._collection.count(),
            "message": f"PDF procesado y indexado exitosamente"
        }
    
    def similarity_search(self, query: str, k: int = None, document_name: str = None) -> List[Document]:
        """
        Realiza búsqueda de similitud en la base vectorial.
        
        PROCESO DE BÚSQUEDA VECTORIAL:
        1. La query del usuario se convierte a vector (mismo modelo de embeddings)
        2. Se calcula similitud con TODOS los vectores en la base
        3. Se retornan los k más similares (top-k)
        
        Args:
            query: Pregunta del usuario
            k: Cantidad de resultados a retornar (default: settings.TOP_K_RESULTS)
            document_name: Nombre del documento específico a buscar (opcional)
            
        Returns:
            Lista de documentos más similares
        """
        k = k or settings.TOP_K_RESULTS
        
        print(f"\n🔍 Buscando en base vectorial: '{query}'")
        print(f"   Top-k: {k}")
        if document_name:
            print(f"   Filtrando por documento: {document_name}")
        
        # Si se especifica un documento, filtrar los resultados después de buscar
        all_results = self.vector_store.similarity_search(
            query=query,
            k=k * 3  # Buscar más para tener suficientes después de filtrar
        )
        
        # Filtrar por documento si se especifica
        if document_name:
            filtered_results = [
                doc for doc in all_results 
                if doc.metadata.get("source") == document_name
            ]
            print(f"   ✅ Encontrados {len(filtered_results)} documentos en '{document_name}'")
            return filtered_results[:k]
        
        print(f"   ✅ Encontrados {len(all_results)} documentos relevantes")
        
        return all_results[:k]
    
    def generate_response(self, query: str, context_docs: List[Document]) -> str:
        """
        Genera una respuesta usando el LLM con el contexto recuperado.
        
        PROMPT CONSTRUCTION:
        El prompt típico para RAG sigue este formato:
        
        ```
        Eres un asistente útil. Responde basándote únicamente en el siguiente contexto.
        
        Contexto:
        [chunk 1]
        ---
        [chunk 2]
        ---
        
        Pregunta: {query}
        
        Respuesta:
        ```
        
        Args:
            query: Pregunta del usuario
            context_docs: Documentos recuperados de la búsqueda vectorial
            
        Returns:
            Respuesta generada por el LLM
        """
        # Construir contexto desde los documentos retrieved
        context = "\n\n---\n\n".join([doc.page_content for doc in context_docs])
        
        # Armar el prompt con el historial de conversación
        conversation_context = self._build_conversation_context()
        
        # Prompt completo
        prompt = f"""Eres un asistente útil especializado en analizar documentos PDF.
Responde basándote ÚNICAMENTE en el contexto proporcionado. 
Si no tienes información suficiente para responder, indicate que no tienes esa información en el contexto.

{conversation_context}
Contexto relevante extraído del documento:
{context}

Pregunta: {query}

Respuesta:"""
        
        print(f"🤖 Enviando prompt al LLM ({len(prompt)} caracteres)...")
        
        try:
            # Invocar el LLM con timeout más largo
            response = self._llm.invoke(prompt)
            
            # Extraer el contenido de la respuesta
            answer = response.content if hasattr(response, 'content') else str(response)
            
            print(f"   ✅ Respuesta generada ({len(answer)} caracteres)")
            
            return answer
            
        except Exception as llm_error:
            error_msg = str(llm_error)
            print(f"   ❌ Error del LLM: {error_msg}")
            
            # Si Ollama no está corriendo, dar un mensaje más claro
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                return "⚠️ El servicio de Ollama no está disponible. Asegúrate de tener Ollama corriendo con 'ollama serve' y el modelo descargado con 'ollama pull llama2'."
            
            # Si timeout, dar mensaje de retry
            if "timeout" in error_msg.lower():
                return "⚠️ El modelo está tardando mucho en responder. Podés esperar un poco más o intentar con una pregunta más simple."
            
            # Error genérico
            return f"⚠️ Hubo un error al generar la respuesta: {error_msg}"
    
    def _build_conversation_context(self) -> str:
        """
        Construye el contexto de la conversación desde el historial.
        
        Esto permite que el chat tenga memoria de preguntas anteriores.
        Mantiene los últimos MAX_HISTORY_MESSAGES intercambios.
        
        Returns:
            String con el historial formateado
        """
        if not self.conversation_history:
            return ""
        
        # Tomar los últimos mensajes
        recent_history = self.conversation_history[-settings.MAX_HISTORY_MESSAGES:]
        
        context_lines = ["Historial de conversación:"]
        for msg in recent_history:
            context_lines.append(f"Usuario: {msg['user']}")
            context_lines.append(f"Asistente: {msg['assistant']}")
        
        return "\n".join(context_lines) + "\n\n"
    
    def query(self, question: str, document_name: str = None) -> Dict[str, Any]:
        """
        Pipeline completo de consulta al sistema RAG.
        
        1. Buscar documentos relevantes (retrieval)
        2. Generar respuesta con LLM (generation)
        3. Guardar en historial
        
        Args:
            question: Pregunta del usuario
            document_name: Nombre específico del documento a consultar (opcional)
            
        Returns:
            Dict con respuesta, documentos fuente, etc.
        """
        print(f"\n💬 Nueva consulta: {question}")
        if document_name:
            print(f"   📄 Documento específico: {document_name}")
        
        # Paso 1: Retrieval - buscar documentos relevantes
        relevant_docs = self.similarity_search(query=question, document_name=document_name)
        
        if not relevant_docs:
            if document_name:
                return {
                    "answer": f"No encontré información relevante en '{document_name}'. "
                             "Probá con otra pregunta o seleccioná otro documento.",
                    "sources": [],
                    "conversation_history": self.conversation_history
                }
            return {
                "answer": "No encontré información relevante en los documentos cargados. "
                         "Por favor asegurate de haber subido un PDF primero.",
                "sources": [],
                "conversation_history": self.conversation_history
            }
        
        # Paso 2: Generation - generar respuesta
        answer = self.generate_response(question, relevant_docs)
        
        # Paso 3: Guardar en historial
        self.conversation_history.append({
            "user": question,
            "assistant": answer
        })
        
        # Limitar tamaño del historial
        if len(self.conversation_history) > settings.MAX_HISTORY_MESSAGES * 2:
            self.conversation_history = self.conversation_history[-settings.MAX_HISTORY_MESSAGES * 2:]
        
        # Retornar resultado con metadata adicional
        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in relevant_docs
            ],
            "conversation_history": self.conversation_history
        }
    
    def reset_conversation(self):
        """Limpia el historial de conversación."""
        self.conversation_history = []
        print("🗑️ Historial de conversación limpiado")
    
    def get_documents_list(self) -> List[Dict[str, Any]]:
        """
        Retorna una lista de los documentos indexados.
        
        Returns:
            Lista de documentos con su metadata
        """
        if not self._vector_store:
            return []
        
        # Obtener todos los documentos (usando get)
        try:
            # Nueva API de ChromaDB 1.x
            results = self._vector_store.get()
            
            if not results or not results.get("metadatas"):
                return []
            
            # Extraer nombres únicos de documentos
            documents = []
            seen = set()
            
            for i, metadata in enumerate(results.get("metadatas", [])):
                if metadata:
                    source = metadata.get("source", "Unknown")
                    if source not in seen:
                        seen.add(source)
                        documents.append({
                            "name": source,
                            "indexed_at": metadata.get("timestamp", "Unknown")
                        })
            
            return documents
        except Exception as e:
            print(f"Error al obtener lista de documentos: {e}")
            return []
    
    def delete_document(self, document_name: str) -> Dict[str, Any]:
        """
        Elimina un documento específico de la base vectorial.
        
        Args:
            document_name: Nombre del documento a eliminar
            
        Returns:
            Dict con el resultado de la operación
        """
        if not self._vector_store:
            return {"status": "error", "message": "No hay documentos en la base"}
        
        try:
            # Decodificar el nombre del documento
            import urllib.parse
            document_name = urllib.parse.unquote(document_name)
            
            print(f"🗑️ Eliminando documento: {document_name}")
            
            # Obtener todos los documentos
            results = self._vector_store.get()
            
            if not results or not results.get("metadatas"):
                return {"status": "error", "message": "No hay documentos"}
            
            metadatas = results.get("metadatas", [])
            ids = results.get("ids", [])
            
            # Encontrar los IDs a eliminar
            ids_to_delete = []
            deleted_count = 0
            
            for i, metadata in enumerate(metadatas):
                if metadata and metadata.get("source") == document_name:
                    if i < len(ids):
                        ids_to_delete.append(ids[i])
                        deleted_count += 1
            
            if not ids_to_delete:
                return {"status": "error", "message": f"Documento '{document_name}' no encontrado"}
            
            # Eliminar usando delete
            self._vector_store.delete(ids=ids_to_delete)
            
            print(f"   ✅ Eliminados {deleted_count} chunks")
            
            return {
                "status": "success",
                "message": f"Documento '{document_name}' eliminado",
                "deleted_chunks": deleted_count
            }
            
        except Exception as e:
            print(f"Error al eliminar documento: {e}")
            return {"status": "error", "message": str(e)}
            
            self._vector_store.persist()
            
            return {
                "status": "success",
                "message": f"Documento '{document_name}' eliminado ({deleted_count} chunks)",
                "remaining_documents": self._vector_store._collection.count()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """
        Elimina todos los documentos de la base vectorial.
        
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Crear nueva base vacía
            self._vector_store = Chroma(
                persist_directory=str(settings.CHROMA_DB_PATH),
                embedding_function=self._embeddings
            )
            self._vector_store.persist()
            
            return {
                "status": "success",
                "message": "Todos los documentos eliminados"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la base de datos vectorial."""
        if self._vector_store:
            count = self._vector_store._collection.count()
        else:
            count = 0
        
        return {
            "total_documents": count,
            "embedding_model": settings.EMBEDDINGS_MODEL,
            "llm_provider": settings.LLM_PROVIDER,
            "llm_model": settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.OPENAI_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k": settings.TOP_K_RESULTS
        }


# ========================================
# INSTANCIA GLOBAL DEL SERVICIO RAG
# ========================================
# Se crea una sola instancia que se reutiliza en toda la app
rag_service = RAGService()