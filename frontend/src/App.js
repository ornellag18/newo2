import React, { useState, useEffect } from 'react';
import SideBar from './components/SideBar';
import ChatContainer from './components/ChatContainer';
import './App.css';

function App() {
  const [sessions, setSessions] = useState([]); // Manejo de sesiones
  const [currentSession, setCurrentSession] = useState(null); // Sesión seleccionada
  const [chatHistory, setChatHistory] = useState([]); // Mensajes de la sesión seleccionada

  // Cargar historial de sesiones al montar el componente
  useEffect(() => {
    fetch('http://127.0.0.1:5001/historial')
      .then(response => response.json())
      .then(data => {
        if (data.historial) {
          const uniqueSessions = data.historial
            .map(item => ({
              session_id: item.session_id,
              query: item.query
            }));
            setSessions(uniqueSessions);
            setCurrentSession(uniqueSessions[0]?.session_id || null);
        }
      })
      .catch(error => console.error('Error fetching sessions:', error));
  }, []);

  const loadChatHistory = (sessionId) => {
    if (!sessionId) {
      setChatHistory([]);
      return;
    }
    if (!sessionId) {
      console.error("sessionId es undefined o null");
      return;
  }
    fetch(`http://127.0.0.1:5001/get_chat_history/${encodeURIComponent(sessionId)}`)
      .then(response => response.json())
      .then(data => setChatHistory(data))
      .catch(error => console.error('Error fetching chat history:', error));
  }
  // Actualizar el historial al cambiar de sesión
  useEffect(() => {
    loadChatHistory(currentSession);
  }, [currentSession]);

  return (
    <div className="container">
      <SideBar sessions={sessions} setCurrentSession={setCurrentSession} />
      {/* Asegúrate de pasar setMessages como prop */}
      <ChatContainer session={currentSession} messages={chatHistory} setMessages={setChatHistory} />
    </div>
  );
}

export default App;
