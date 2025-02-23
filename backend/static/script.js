$(document).ready(function() {
    // Cargar la lista de historial
    $.get('/historial', function(data) {
        if (data.historial && data.historial.length > 0) {
            let sessions = new Set();
            data.historial.forEach(function(item) {
                let session = item.session_id;
                sessions.add(session);
            });

            sessions.forEach(function(session) {
                // Buscar la consulta correspondiente al session_id
                let query = data.historial.find(item => item.session_id === session).query;
                $('#history-list').append(`<li class="history-item" data-session="${session}">${query}</li>`);
            });

            // Cargar el historial de la primera sesión (opcional)
            if (sessions.size > 0) {
                loadChatHistory([...sessions][0]);
            }
        }
    });

    // Manejar clic en el botón de nueva sesión
    $('#new-session-button').click(function() {
        // Limpiar el área de chat
        $('#chat-container').empty(); 
        sessionStorage.removeItem('session_id');
        // (Opcional) Puedes limpiar también algún campo de entrada o indicar visualmente que se inició una nueva sesión.
    });
    
    
    
    function loadChatHistory(sessionId) {
        if (!sessionId) {
            console.error("sessionId es undefined o null");
            return;
        }
        $.ajax({
            url: `/get_chat_history/${sessionId}`,  // Endpoint correcto en Flask
            method: 'GET',
            success: function(data) {
                $('#chat-container').empty();  // Limpiar el historial anterior
                if (data.length > 0) {
                    data.forEach(function(chat) {
                        if (chat.type === "query") {
                            $('#chat-container').append(`
                                <div class="message-wrapper">
                                    <div class="message query">${chat.content}</div>
                                </div>
                            `);
                        } else if (chat.type === "response") {
                            $('#chat-container').append(`
                                <div class="message-wrapper">
                                    <div class="message response">${chat.content}</div>
                                </div>
                            `);
                        }
                    });
                } else {
                    $('#chat-container').append('<p>No hay mensajes en esta sesión.</p>');
                }
                // Scroll hacia el final para mostrar los últimos mensajes
                $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
            },
            error: function(xhr, status, error) {
                console.error('Error cargando historial de la sesión:', error);
            }
        });
    }

    $(document).on('click', '.history-item', function() {
        $('.history-item').removeClass('selected');  // Desmarcar otras sesiones
        $(this).addClass('selected');  // Marcar la sesión seleccionada
        let selectedSession = $(this).data('session');
        if (!selectedSession) {
            console.error("No se pudo obtener el session_id del elemento seleccionado");
            return;
        }
        sessionStorage.setItem('session_id', selectedSession);
        loadChatHistory(selectedSession);
    });

    // Enviar la consulta con el session_id seleccionado
    function handleSubmit() {
        const submitButton = $('#submit-button');
        const spinner = $('#loading-spinner');
        
        submitButton.prop('disabled', true);
        submitButton.addClass('loading');
        spinner.show();
    
        const query = $('#query-input').val();
        const assistanceType = $('#assistance-type').val();
        const modelType = $('#model-type').val();
        let session_id = sessionStorage.getItem('session_id'); // Obtener la sesión actual
    
        // Si no hay session_id, es una nueva sesión
        const isNewSession = session_id ? false : true;
    
        $.ajax({
            type: 'POST',
            url: '/query',
            contentType: 'application/json',
            data: JSON.stringify({
                query: query,
                assistance_type: assistanceType,
                model_type: modelType,
                session_id: session_id,
                is_new_session: isNewSession
            }),
            success: function(response) {
                // Si se ha creado una nueva sesión, guarda el session_id
                if (isNewSession) {
                    sessionStorage.setItem('session_id', response.session_id);
                }
                // Mostrar consulta
                $('#chat-container').append(`
                    <div class="message-wrapper">
                        <div class="message query">
                            ${query}
                        </div>
                    </div>
                `);
                // Mostrar respuesta
                $('#chat-container').append(`
                    <div class="message-wrapper">
                        <div class="message response">
                            ${response.result}
                        </div>
                    </div>
                `);
                $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
                $('#query-input').val('');
                submitButton.prop('disabled', false);
                submitButton.removeClass('loading');
                spinner.hide();
            },
            error: function(xhr, status, error) {
                console.error('Error en la solicitud:', error);
                submitButton.prop('disabled', false);
                submitButton.removeClass('loading');
                spinner.hide();
            }
        });
    }
    
    $('#submit-button').on('click', function() {
        handleSubmit();
    });
    
    $('#query-input').on('keypress', function(e) {
        if (e.which == 13) {
            handleSubmit();
        }
    });    
});