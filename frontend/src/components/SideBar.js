import React from 'react';

function SideBar({ sessions, setCurrentSession }) {
  return (
    <div className="sidebar">
      <div className="historial-header">
        <h2>Historial</h2>
        <button 
          id="new-session-button"
          onClick={() => setCurrentSession(null)} // Al hacer clic, se crea una nueva sesión
        >
          Nueva Sesión
        </button>
      </div>
      <ul id="history-list">
        {sessions.map((session, index) => (
    <li key={index} onClick={() => setCurrentSession(session.session_id)}>
      {session.query || "Sesión sin título"} {/* Mostrar el contenido del query */}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SideBar;
