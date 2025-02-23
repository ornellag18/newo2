fetch('http://127.0.0.1:5001/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: userQuery, // 'query' es obligatorio
      assistance_type: 'default', // Valor por defecto según tu Flask
      session_id: '', // Inicialmente vacío si es nueva sesión
      is_new_session: true, // Indica si es una nueva sesión
    }),
  });
  