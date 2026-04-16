/**
 * =========================================
 * SERVICIO API - COMUNICACIÓN CON BACKEND
 * =========================================
 * Maneja todas las peticiones HTTP al servidor FastAPI.
 * Usa Axios para las solicitudes.
 */

import axios from 'axios';

// URL base del backend (configurable via env var)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Crear instancia de Axios con configuración por defecto
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutos - necesario para PDFs grandes y generación de respuesta con LLM
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('❌ Error API:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * =========================================
 * ENDPOINTS DEL BACKEND
 * =========================================
 */

// 1. Health Check - verificar si el backend está online
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend no disponible');
  }
};

// 2. Obtener estadísticas del sistema
export const getStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * =========================================
 * UPLOAD DE PDF
 * =========================================
 * Envía un archivo PDF al endpoint /upload
 * El backend procesa el PDF y lo indexa en ChromaDB
 * 
 * @param {File} file - Archivo PDF a subir
 * @param {Function} onProgress - Callback para progreso (opcional)
 * @returns {Promise} Respuesta del backend
 */
export const uploadPDF = async (file, onProgress = null) => {
  try {
    // Crear FormData para envío de archivos
    const formData = new FormData();
    formData.append('file', file);

    // Configurar solicitud con callback de progreso
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    };

    const response = await api.post('/upload', formData, config);
    return response.data;
  } catch (error) {
    if (error.response) {
      // Error del servidor (código 4xx o 5xx)
      const message = error.response.data?.detail || 'Error al subir el PDF';
      throw new Error(message);
    } else if (error.request) {
      // No hubo respuesta del servidor
      throw new Error('El servidor no respondió. Verificá que esté corriendo.');
    } else {
      // Error de configuración
      throw new Error('Error al configurar la solicitud: ' + error.message);
    }
  }
};

/**
 * =========================================
 * CONSULTA AL CHAT
 * =========================================
 * Envía una pregunta al endpoint /query
 * El backend busca en ChromaDB y genera respuesta con LLM
 * 
 * @param {string} question - Pregunta del usuario
 * @param {string} documentName - Nombre específico del documento (opcional)
 * @returns {Promise} Respuesta del LLM + documentos fuente
 */
export const sendMessage = async (question, documentName = null) => {
  try {
    const payload = { question: question };
    if (documentName) {
      payload.document_name = documentName;
    }
    const response = await api.post('/query', payload);
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data?.detail || 'Error al procesar la consulta';
      throw new Error(message);
    } else if (error.request) {
      throw new Error('El servidor no respondío.');
    } else {
      throw new Error('Error al enviar el mensaje: ' + error.message);
    }
  }
};

/**
 * =========================================
 * RESETEAR CONVERSACIÓN
 * =========================================
 */
export const resetConversation = async () => {
  try {
    const response = await api.post('/reset');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * =========================================
 * LISTAR DOCUMENTOS
 * =========================================
 */
export const getDocuments = async () => {
  try {
    const response = await api.get('/documents');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * =========================================
 * ELIMINAR DOCUMENTO
 * =========================================
 */
export const deleteDocument = async (documentName) => {
  try {
    const response = await api.delete(`/documents/${encodeURIComponent(documentName)}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * =========================================
 * ELIMINAR TODOS LOS DOCUMENTOS
 * =========================================
 */
export const clearAllDocuments = async () => {
  try {
    const response = await api.delete('/documents');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * =========================================
 * OBTENER ARCHIVO PDF
 * =========================================
 * Retorna la URL del archivo PDF para visualizarlo
 */
export const getFileUrl = (filename) => {
  return `${API_BASE_URL}/files/${encodeURIComponent(filename)}`;
};

export default api;