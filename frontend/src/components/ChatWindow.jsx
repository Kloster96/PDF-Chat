/**
 * =========================================
 * CHAT WINDOW - INTERFAZ DE CHAT ESTILO CHATGPT
 * =========================================
 * Muestra el historial de mensajes con diferenciación
 * entre usuario y AI. Incluye input para enviar preguntas.
 */

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2, FileText, Loader2 } from 'lucide-react';

const ChatWindow = ({ messages, onSendMessage, onReset, hasDocument, isLoading, selectedDocument }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll al final cuando hay nuevos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Maneja el envío del mensaje
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const trimmedMessage = inputValue.trim();
    if (!trimmedMessage) return;

    setInputValue('');
    await onSendMessage(trimmedMessage);
  };

  /**
   * Maneja la tecla Enter
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-dark-950">
      {/* Header del Chat */}
      <header className="h-14 px-6 flex items-center justify-between border-b border-dark-700 bg-dark-900">
        <div className="flex items-center gap-3">
          <Bot className="w-5 h-5 text-accent-400" />
          <h1 className="text-dark-100 font-semibold">Asistente PDF</h1>
        </div>
        
        <button
          onClick={onReset}
          className="p-2 text-dark-400 hover:text-dark-200 hover:bg-dark-800 rounded-lg transition-colors"
          title="Limpiar conversación"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </header>

      {/* Área de Mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Mensaje de bienvenida / instructivo */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-16 h-16 rounded-full bg-dark-800 flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-dark-500" />
            </div>
            <h2 className="text-xl font-semibold text-dark-200 mb-2">
              Chat con tus documentos PDF
            </h2>
            <p className="text-dark-400 max-w-md">
              {selectedDocument 
                ? `Consultando: ${selectedDocument}. Escribí tu pregunta.`
                : hasDocument 
                  ? 'Escribí una pregunta sobre el documento cargado y te ayudaré a encontrar la información. También podés seleccionar un documento específico del sidebar.'
                  : 'Subí un PDF en el panel lateral para comenzar a chatear con su contenido.'}
            </p>
          </div>
        )}

        {/* Historial de mensajes */}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
              ${message.role === 'user' ? 'bg-accent-600' : 'bg-dark-700'}
            `}>
              {message.role === 'user' 
                ? <User className="w-4 h-4 text-white" />
                : <Bot className="w-4 h-4 text-accent-400" />
              }
            </div>

            {/* Bubble de mensaje */}
            <div className={`
              ${message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}
            `}>
              {/* Nombre del rol (opcional, para claridad) */}
              <p className={`
                text-xs font-medium mb-1
                ${message.role === 'user' ? 'text-accent-200' : 'text-dark-400'}
              `}>
                {message.role === 'user' ? 'Vos' : 'AI'}
              </p>
              
              {/* Contenido del mensaje */}
              <p className="whitespace-pre-wrap leading-relaxed">
                {message.content}
              </p>
              
              {/* Fuentes (solo para mensajes de AI) */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-dark-700">
                  <p className="text-xs text-dark-500 mb-2">
                    Fuentes consultadas:
                  </p>
                  <div className="space-y-1">
                    {message.sources.map((source, idx) => (
                      <p key={idx} className="text-xs text-dark-400 truncate">
                        • {source.metadata?.source || `Fragmento ${idx + 1}`}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Indicador de carga */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center">
              <Bot className="w-4 h-4 text-accent-400" />
            </div>
            <div className="chat-bubble-ai flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-dark-400 animate-spin" />
              <span className="text-dark-400">Pensando...</span>
            </div>
          </div>
        )}

        {/* Ref para auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Área de Input */}
      <div className="p-4 border-t border-dark-700 bg-dark-900">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={hasDocument 
              ? 'Escribí tu pregunta sobre el documento...'
              : 'Primero subí un PDF para comenzar'
            }
            disabled={!hasDocument || isLoading}
            className="
              flex-1 bg-dark-800 text-dark-100 placeholder-dark-500
              px-4 py-3 rounded-xl border border-dark-700
              focus:outline-none focus:border-accent-500 focus:ring-1 focus:ring-accent-500
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || !hasDocument || isLoading}
            className="
              px-4 py-3 bg-accent-600 hover:bg-accent-500 
              disabled:bg-dark-700 disabled:text-dark-500 disabled:cursor-not-allowed
              text-white rounded-xl transition-colors
              flex items-center justify-center
            "
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;