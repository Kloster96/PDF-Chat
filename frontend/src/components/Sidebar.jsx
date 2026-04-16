/**
 * =========================================
 * SIDEBAR - PANEL LATERAL DE SUBIDA DE PDFs
 * =========================================
 * Área para arrastrar y soltar PDFs, mostrar progreso,
 * lista de documentos y visualizador de PDF.
 */

import { useState, useCallback, useEffect } from 'react';
import { 
  Upload, FileText, CheckCircle, Loader2, X, AlertCircle, 
  Trash2, Eye, EyeOff, BookOpen, File
} from 'lucide-react';
import { uploadPDF, getDocuments, deleteDocument, getFileUrl } from '../services/api';

const Sidebar = ({ onUploadComplete, isOnline, selectedDocument, onSelectDocument }) => {
  // Estados del componente
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documents, setDocuments] = useState([]);
const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showPdfViewer, setShowPdfViewer] = useState(false);

  // Cargar lista de documentos al iniciar
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoadingDocuments(true);
    try {
      const result = await getDocuments();
      setDocuments(result.documents || []);
    } catch (error) {
      console.error("Error cargando documentos:", error);
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  /**
   * Maneja el evento de arrastrar archivo sobre la zona
   */
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  /**
   * Maneja cuando el archivo sale de la zona de drop
   */
  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

/**
    * Maneja el evento de soltar el archivo
    */
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleMultipleFiles(files);
    }
  }, []);

  /**
   * Maneja la selección de archivo mediante el input (soporta múltiples)
   */
  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files);
    if (files && files.length > 0) {
      handleMultipleFiles(files);
      // Limpiar el input para permitir seleccionar los mismos archivos de nuevo
      e.target.value = '';
    }
  }, []);

  /**
   * Procesa múltiples archivos uno por uno
   */
  const handleMultipleFiles = async (files) => {
    // Filtrar solo PDFs
    const pdfFiles = files.filter(file => 
      file.name.toLowerCase().endsWith('.pdf')
    );
    
    if (pdfFiles.length === 0) {
      setUploadStatus('error');
      setErrorMessage('Solo se aceptan archivos PDF');
      return;
    }
    
    if (pdfFiles.length > 3) {
      setUploadStatus('error');
      setErrorMessage('Máximo 3 PDFs a la vez');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');

    let uploadedCount = 0;
    
    for (let i = 0; i < pdfFiles.length; i++) {
      const file = pdfFiles[i];
      
      // Validar tamaño
      if (file.size > 50 * 1024 * 1024) {
        setErrorMessage(`${file.name} excede el límite de 50MB`);
        continue;
      }

      try {
        await uploadPDF(file, (progress) => {
          // Calcular progreso promedio
          const totalProgress = ((i * 100) + progress) / pdfFiles.length;
          setUploadProgress(Math.round(totalProgress));
        });
        uploadedCount++;
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
      }
    }

    // Recargar lista de documentos
    await loadDocuments();
    
    if (uploadedCount === pdfFiles.length) {
      resetUpload();
    } else if (uploadedCount > 0) {
      setUploadStatus('success');
    } else {
      setUploadStatus('error');
      setErrorMessage('Error al subir los archivos');
    }
  };

  /**
   * Procesa el archivo seleccionado
   */
  const handleFile = async (file) => {
    // Validar que sea PDF
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadStatus('error');
      setErrorMessage('Solo se aceptan archivos PDF');
      return;
    }

    // Validar tamaño (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setUploadStatus('error');
      setErrorMessage('El archivo excede el límite de 50MB');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');

    try {
      // Subir archivo al backend
      const result = await uploadPDF(file, (progress) => {
        setUploadProgress(progress);
      });

      // Recargar lista de documentos
      await loadDocuments();
      
      // Notificar al componente padre
      if (onUploadComplete) {
        onUploadComplete(result);
      }
      
      // Resetear el estado para permitir más uploads
      resetUpload();
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(error.message || 'Error al subir el archivo');
    }
  };

  /**
   * Reinicia el estado de upload y limpia el input file
   */
  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setErrorMessage('');
    // Limpiar el input file
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

/**
   * Elimina un documento
   */
  const handleDeleteDocument = async (docName, e) => {
    e.stopPropagation();
    if (!confirm(`¿Eliminar "${docName}"?`)) return;

    try {
      await deleteDocument(docName);
      await loadDocuments();

      // Si era el seleccionado, notificar al padre para limpiar
      if (selectedDocument === docName && onSelectDocument) {
        onSelectDocument(null);
      }
    } catch (error) {
      alert('Error al eliminar documento');
    }
  };

  // Render de la zona de drop
  const renderDropZone = () => (
    <div
      className={`
        drop-zone cursor-pointer text-center
        ${isDragging ? 'active' : 'hover:border-dark-500 hover:bg-dark-800/50'}
      `}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => document.getElementById('file-input').click()}
    >
      <input
        id="file-input"
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileSelect}
      />
      
      <Upload className="w-10 h-10 mx-auto mb-3 text-dark-500" />
      <p className="text-dark-300 font-medium">
        Arrastrá un PDF aquí
      </p>
      <p className="text-dark-500 text-sm mt-1">
        o hacé clic para buscar
      </p>
    </div>
  );

  // Render del estado de uploading
  const renderUploading = () => (
    <div className="text-center p-6">
      <Loader2 className="w-10 h-10 mx-auto mb-3 text-accent-500 animate-spin" />
      <p className="text-dark-200 font-medium mb-2">
        Indexando documento...
      </p>
      
      {/* Barra de progreso */}
      <div className="w-full bg-dark-700 rounded-full h-2 mb-2">
        <div
          className="bg-accent-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${uploadProgress}%` }}
        />
      </div>
      <p className="text-dark-500 text-xs">
        {uploadProgress}% completado
      </p>
    </div>
  );

  // Render del estado de error
  const renderError = () => (
    <div className="p-4 bg-red-900/20 rounded-xl border border-red-800">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-red-400 font-medium">
            Error al subir archivo
          </p>
          <p className="text-dark-400 text-sm mt-1">
            {errorMessage}
          </p>
          <button
            onClick={resetUpload}
            className="mt-3 text-accent-400 hover:text-accent-300 text-sm font-medium"
          >
            Intentar de nuevo
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <aside className="w-96 bg-dark-900 border-r border-dark-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-dark-700">
        <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-accent-400" />
          Documentos
        </h2>
        
        {/* Indicador de conexión */}
        <div className="mt-2 flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-dark-400">
            {isOnline ? 'Backend online' : 'Backend offline'}
          </span>
        </div>
      </div>

      {/* Área de Upload - solo mostrar si no hay documentos o en estado idle/uploading */}
      <div className="p-4 border-b border-dark-700">
        {uploadStatus === 'idle' && renderDropZone()}
        {uploadStatus === 'uploading' && renderUploading()}
        {uploadStatus === 'success' && (
          <button
            onClick={resetUpload}
            className="w-full p-3 bg-dark-800 hover:bg-dark-700 rounded-xl border border-dark-600 text-dark-300 flex items-center justify-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Subir otro PDF
          </button>
        )}
        {uploadStatus === 'error' && renderError()}
      </div>

      {/* Lista de documentos */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-dark-300 font-medium">Documentos ({documents.length})</h3>
          {documents.length > 0 && (
            <button
              onClick={() => {
                if (confirm('¿Eliminar todos los documentos?')) {
                  // Implementar clear all
                }
              }}
              className="text-dark-500 hover:text-red-400 text-xs"
            >
              Limpiar todo
            </button>
          )}
        </div>

        {isLoadingDocuments ? (
          <div className="text-center text-dark-500 py-4">
            <Loader2 className="w-6 h-6 mx-auto animate-spin" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center text-dark-500 py-8">
            <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No hay documentos</p>
            <p className="text-xs mt-1">Subí un PDF para comenzar</p>
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.name}
                onClick={() => {
                  onSelectDocument(doc.name);
                  setShowPdfViewer(true);
                }}
                className={`
                  p-3 rounded-xl border cursor-pointer transition-all
                  ${selectedDocument === doc.name 
                    ? 'bg-accent-900/30 border-accent-500' 
                    : 'bg-dark-800 border-dark-700 hover:border-dark-600'
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-accent-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-dark-200 font-medium truncate">
                      {doc.name}
                    </p>
                    <p className="text-dark-500 text-xs mt-1">
                      Indexado: {new Date(doc.indexed_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteDocument(doc.name, e)}
                    className="text-dark-500 hover:text-red-400 p-1"
                    title="Eliminar"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Visualizador de PDF */}
      {showPdfViewer && selectedDocument && (
        <div className="border-t border-dark-700 h-64">
          <div className="flex items-center justify-between p-2 bg-dark-800 border-b border-dark-700">
            <span className="text-dark-300 text-sm truncate px-2">
              {selectedDocument}
            </span>
            <button
              onClick={() => setShowPdfViewer(false)}
              className="text-dark-400 hover:text-dark-200 p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <iframe
            src={getFileUrl(selectedDocument)}
            className="w-full h-full"
            title={selectedDocument}
          />
        </div>
      )}

      {/* Footer con ayuda */}
      <div className="p-4 border-t border-dark-700">
        <p className="text-dark-500 text-xs text-center">
          Múltiples PDFs soportados<br />
          Seleccioná uno para ver
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;