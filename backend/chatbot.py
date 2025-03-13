from flask import jsonify, request
from openai import OpenAI 
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory
from .response_formatting import text_to_html_list, serialize_memory
from vector_search import perform_mongo_search
from mongo_connection import get_mongo_collections
from datetime import datetime
from bson.objectid import ObjectId
import os


# Inicializar clientes de IA
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
deepseek_client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")  # Asume que tienes una clave para DeepSeek
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def handle_query(request):
    try:
        data = request.json
        user_query = data.get('query', '')
        assistance_type = data.get('assistance_type', 'default')
        model_type = data.get('model_type', 'openai')  # Nuevo campo para seleccionar el modelo
        session_id = data.get('session_id')
        is_new_session = data.get('is_new_session', False)
        

        
        collection, history_collection = get_mongo_collections()
        session_identifier = " ".join(user_query.split()[:3])

        R_info, documents_used, docs = perform_mongo_search(user_query)

        if not docs:
            return jsonify({'result': "No encontré información relevante. Prueba con otra consulta."})

        system_message = "You are a chatbot that provides professional assistance."
        if assistance_type == "industrial_maintenance":
            system_message = "You are a chatbot for industrial maintenance. Provide step-by-step guidance."

        causes_list = []
        solutions_list = []

        for doc in docs:
            if isinstance(doc.get("causes"), list):
                causes_list.extend(doc["causes"])

            if isinstance(doc.get("solutions"), list):
                solutions_list.extend([s.get("description", "Sin descripción") for s in doc["solutions"]])

        Prompt = (
            f"User Query: {user_query}\n\n"
            f"Based strictly on the retrieved document, provide a structured response.\n\n"
            f"🔹 Problem Description: {docs[0].get('description', 'No description available')}\n\n"
            f"🔹 Possible Causes: {', '.join(docs[0].get('causes', []))}\n\n"
            f"🔹 Recommended Solutions:\n"
            + "\n".join(f"Step {sol['step']['$numberInt']}: {sol['description']}" for sol in docs[0].get("solutions", []))
            + "\n\nEnsure that the response is clear, concise, and maintains the structure of the provided document."
        )

        memory_messages = memory.load_memory_variables({}).get('chat_history', [])
    

        messages = (
            [{"role": "system", "content": system_message}] +
            serialize_memory(memory_messages) +
            [{"role": "user", "content": Prompt}]
        )

        # Llamada a la API según el modelo seleccionado
        if model_type == "openai":
            print("Using OpenAI...")
            completion = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # Se utiliza la variable messages
                temperature=0.0, 
                max_tokens=500
            )
            assistant_response = f"[OpenAI] {completion.choices[0].message.content}"
        elif model_type == "deepseek":
            print("Using DeepSeek...")
            completion = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,  # Utilizando el mismo orden de mensajes
                temperature=0.0, 
                max_tokens=500,
                stream=False
            )
            assistant_response = f"[DeepSeek] {completion.choices[0].message.content}"
        else:
            print("Unknown model type. Defaulting to OpenAI.")
            assistant_response = "Model not recognized. Using OpenAI by default."

        assistant_response_html = text_to_html_list(assistant_response)
        memory.save_context({"input": user_query}, {"output": assistant_response})


        response_with_sources = f"{assistant_response_html}<br><strong>Documents Used:</strong><br>" + "<br>".join(documents_used)
        timestamp = datetime.now().isoformat()

        if is_new_session or not session_id:
            session_id = history_collection.insert_one({
                "session_identifier": session_identifier,
                "query": user_query,
                "response": response_with_sources,
                "timestamp": timestamp,
                "responses": []
            }).inserted_id
        else:
            history_collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$push": {"responses": {"query": user_query, "response": response_with_sources, "timestamp": timestamp}}},
                upsert=True
            )

        return jsonify({'result': response_with_sources, 'session_id': str(session_id)})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal Server Error'}), 500