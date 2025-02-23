import React, { useState, useEffect } from 'react';

function ChatContainer({ session, messages, setMessages }) {
  const [isLoading, setIsLoading] = useState(false); // Indica si está cargando

  // Cargar historial de chat cuando cambia la sesión
  useEffect(() => {
    if (session) {
      fetch(`http://127.0.0.1:5001/get_chat_history/${encodeURIComponent(session)}`)
        .then(response => response.json())
        .then(data => {
          // Establecer los mensajes con el historial completo
          setMessages(data);
        })
        .catch(error => console.error('Error fetching chat history:', error));
    }
  }, [session, setMessages]);

  const handleSendMessage = async () => {
    const query = document.getElementById('query-input').value;
    const assistanceType = document.getElementById('assistance-type').value;
  
    if (!query.trim()) return;
  
    // Agregar la consulta al estado
    setMessages(prevMessages => [...prevMessages, { type: 'query', content: query }]);
  
    document.getElementById('query-input').value = '';
  
    const requestPayload = {
      query: query,
      assistance_type: assistanceType,
      session_id: session, // 'session' viene como prop; puede ser null si no hay sesión
      is_new_session: session ? false : true,
    };
  
    setIsLoading(true);
  
    try {
      const response = await fetch('http://127.0.0.1:5001/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload),
      });
  
      const result = await response.json();
  
      if (response.ok && result.result) {
        // Si es una nueva sesión, actualizar el session id (podrías levantar esto a un callback en App.js)
        if (!session) {
          // Aquí se debería actualizar el estado de la sesión en el componente padre
        }
        // Agregar la respuesta al estado
        setMessages(prevMessages => [...prevMessages, { type: 'response', content: result.result }]);
      } else {
        console.error('Error del servidor al enviar el mensaje.');
      }
    } catch (error) {
      console.error('Error en la comunicación con el servidor:', error);
    } finally {
      setIsLoading(false);
    }
  };
  

  return (
    <div className="main-content">
      <img src="/static/images/newo_logo.png" alt="Newo Logo" className="logo" />
      <div id="chat-container" className="chat-container">
        {messages.length > 0 ? (
          messages.map((message, index) => (
            <div key={index} className={`message-wrapper ${message.type}`}>
              <div className={message.type === 'query' ? 'message query' : 'message response'}>
                {message.content}
              </div>
            </div>
          ))
        ) : (
          <div>No hay mensajes para esta sesión.</div>
        )}
      </div>
      <div className="input-area">
        <select id="assistance-type">
          <option value="default">Default Assistant</option>
          <option value="industrial_maintenance">Industrial Maintenance</option>
          <option value="technical_support">Technical Support</option>
        </select>
        <input type="query" id="query-input" placeholder="Enter your query" />
        <button id="submit-button" onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? <div id="loading-spinner"></div> : 'Enviar'}
        </button>
      </div>
    </div>
  );
}

export default ChatContainer;