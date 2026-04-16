"""
========================================
PROCESAMIENTO DE PDFs - EXTRACCIÓN Y CHUNKING
========================================
Este módulo se encarga de:
1. Extraer texto de archivos PDF
2. Dividir el texto en fragmentos (chunks) manejables

El CHUNKING es fundamental para el RAG porque:
- Los LLMs tienen límite de tokens (context window)
- Un chunk muy grande diluye la información relevante
- Un chunk muy pequeño pierde contexto
- La superposición (overlap) mantiene coherencia entre chunks
"""

from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class PDFProcessor:
    """
    Procesador de PDFs que extrae texto y lo fragmenta en chunks.
    """
    
    def __init__(self):
        """
        Inicializa el divisor de texto con configuración centralizada.
        
        El RecursiveCharacterTextSplitter funciona así:
        1. Intenta dividir por el primer separador (parrafos \n\n)
        2. Si el chunk es muy grande, intenta con el siguiente (\n)
        3. Y así sucesivamente hasta llegar a caracteres sueltos
        
        Esto preserva la estructura semántica del texto.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,  # Contar caracteres
            separators=settings.CHUNK_SEPARATORS,
            add_start_index=True   # Guardar posición original del chunk
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae todo el texto de un archivo PDF.
        
        Proceso:
        1. Abre el PDF con PdfReader
        2. Itera página por página
        3. Extrae el texto de cada página
        4. Concatena todo en un solo string
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Texto completo del PDF como string
        """
        print(f"📄 Extrayendo texto de: {pdf_path}")
        
        reader = PdfReader(pdf_path)
        full_text = ""
        
        # metadata opcional
        metadata = reader.metadata
        if metadata:
            print(f"   Título: {metadata.get('/Title', 'N/A')}")
            print(f"   Páginas: {len(reader.pages)}")
        
        # Extraer texto de cada página
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        print(f"   Caracteres extraídos: {len(full_text)}")
        return full_text
    
    def create_chunks(self, text: str) -> List[str]:
        """
        Divide el texto en fragmentos (chunks) usando RecursiveCharacterTextSplitter.
        
        ¿POR QUÉ RecursiveCharacterTextSplitter?
        ----------------------------------------
        A diferencia de un splitter simple que corta por caracteres exactos,
        este algoritmo intenta respetar límites semánticos:
        
        1. Primero intenta separar por párrafos (\n\n)
        2. Si el chunk es muy grande, usa saltos de línea (\n)
        3. Luego espacios
        4. Finalmente caracteres individuales si es necesario
        
        Esto evita que corte a mitad de una oración o párrafo.
        
        Args:
            text: Texto completo a fragmentar
            
        Returns:
            Lista de strings (chunks)
        """
        print(f"✂️  Creando chunks (size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
        
        chunks = self.text_splitter.split_text(text)
        
        print(f"   ✅ Creados {len(chunks)} chunks")
        
        # Mostrar ejemplo del primer chunk
        if chunks:
            print(f"   📝 Ejemplo chunk[0] ({len(chunks[0])} chars): {chunks[0][:100]}...")
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Pipeline completo: extrae texto del PDF y lo divide en chunks.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de chunks listos para indexing en ChromaDB
        """
        # Paso 1: Extraer texto
        text = self.extract_text_from_pdf(pdf_path)
        
        # Paso 2: Crear chunks
        chunks = self.create_chunks(text)
        
        return chunks


# ========================================
# INSTANCIA GLOBAL DEL PROCESADOR
# ========================================
pdf_processor = PDFProcessor()