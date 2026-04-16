/**
 * =========================================
 * APP.JSX - COMPONENTE PRINCIPAL
 * =========================================
 * Orchestras toda la aplicación: conecta el sidebar,
 * el chat, y la comunicación con el backend.
 */

import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { checkHealth, sendMessage, resetConversation } from './services/api';

function App() {
  // ========================================
  // ESTADOS DE LA APLICACIÓN
  // ========================================
  
  // Estado de conexión con el backend
  const [isOnline, setIsOnline] = useState(false);
  const [isCheckingConnection, setIsCheckingConnection] = useState(true);
  
  // Estado del documento
  const [hasDocument, setHasDocument] = useState(false);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  
  // Estado del chat
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // ========================================
  // EFECTOS (useEffect)
  // ========================================
  
  /**
   * Efecto inicial: Verificar conexión con el backend
   */
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const result = await checkHealth();
        setIsOnline(true);
        console.log('✅ Backend conectado:', result);
      } catch (error) {
        setIsOnline(false);
        console.error('❌ Error de conexión:', error.message);
      } finally {
        setIsCheckingConnection(false);
      }
    };
    
    checkConnection();
    
    // Verificar conexión cada 30 segundos
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // ========================================
  // FUNCIONES HANDLERS
  // ========================================
  
  /**
   * HandleUpload: Callback cuando se completa el upload de un PDF
   * @param {Object} result - Respuesta del backend
   */
  const handleUploadComplete = useCallback((result) => {
    setHasDocument(true);
    setDocumentInfo(result);
    
    // Agregar mensaje de sistema
    setMessages(prev => [
      ...prev,
      {
        role: 'system',
        content: `📄 Documento "${result.filename || 'PDF'}" cargado exitosamente.`
      }
    ]);
  }, []);

  /**
   * HandleSendMessage: Envía la pregunta al backend y agrega la respuesta
   * @param {string} question - Pregunta del usuario
   */
  const handleSendMessage = useCallback(async (question) => {
    if (!question.trim() || isLoading) return;
    
    setIsLoading(true);
    
    try {
      // 1. Agregar mensaje del usuario al historial
      const userMessage = { role: 'user', content: question };
      setMessages(prev => [...prev, userMessage]);
      
      // 2. Enviar al backend y obtener respuesta (con documento seleccionado si hay)
      const response = await sendMessage(question, selectedDocument);
      
      // 3. Agregar respuesta de la AI al historial
      const aiMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      // Manejo de errores
      console.error('❌ Error al enviar mensaje:', error);
      
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Disculpa, ocurrió un error al procesar tu pregunta: ${error.message}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  /**
   * HandleReset: Limpia el historial de conversación
   */
  const handleReset = useCallback(async () => {
    try {
      await resetConversation();
    } catch (error) {
      console.error('Error al resetear:', error);
    }
    
    setMessages([]);
  }, []);

  // ========================================
  // RENDER
  // ========================================
  
  return (
    <div className="flex h-screen bg-dark-950 overflow-hidden">
      {/* Sidebar - Panel de carga de PDFs */}
      <Sidebar 
        onUploadComplete={handleUploadComplete}
        isOnline={isOnline}
        selectedDocument={selectedDocument}
        onSelectDocument={setSelectedDocument}
      />
      
      {/* Chat Window - Área de chat principal */}
      <ChatWindow 
        messages={messages}
        onSendMessage={handleSendMessage}
        onReset={handleReset}
        hasDocument={hasDocument}
        isLoading={isLoading}
        selectedDocument={selectedDocument}
      />
    </div>
  );
}

export default App;