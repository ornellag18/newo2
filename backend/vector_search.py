from langchain_mongodb import MongoDBAtlasVectorSearch
from .mongo_connection import get_mongo_collections
from .environment import embeddings
from flask import jsonify
from bson.objectid import ObjectId

def perform_mongo_search(user_query):
    try:
        collection, _ = get_mongo_collections()
        vs = MongoDBAtlasVectorSearch(collection, embeddings, index_name="vector_index")
        docs = vs.max_marginal_relevance_search(user_query, k=1, lambda_mul=0.0)

# Convertir los documentos a diccionarios antes de acceder a sus atributos
        docs = [dict(doc) for doc in docs]

        R_info = "\n".join(doc.get("text", "Sin contenido") for doc in docs)  
        documents_used = [doc.get("source", "Unknown") for doc in docs]


        return R_info, documents_used, docs  # ✅ Ahora devuelve docs
    except Exception as e:
        raise Exception("Error en búsqueda MongoDB: " + str(e))

    

def get_chat_history(session_id):
    try:
        _, history_collection = get_mongo_collections()  # Asegúrate de importar esto

        print(f"Recibido session_id: {session_id}")  # Log para depurar
        session = history_collection.find_one({"_id": ObjectId(session_id)}) # Convertir session_id a ObjectId
        if not session_id or session_id == "undefined":
            return jsonify({'error': 'session_id no proporcionado'}), 400 
        if session:
            # Crear el historial combinando el primer query/response con las respuestas adicionales
            chat_history = [
                {"type": "query", "content": session.get("query")},
                {"type": "response", "content": session.get("response")}
            ]
            # Agregar las respuestas adicionales (respuestas dentro de 'responses')
            for resp in session.get('responses', []):
                chat_history.append({"type": "query", "content": resp['query']})
                chat_history.append({"type": "response", "content": resp['response']})

            return jsonify(chat_history)
        else:
            print("Sesión no encontrada.")
            return jsonify([])
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500


def show_history():
    try:
        _, history_collection = get_mongo_collections()
        # Ordenar por timestamp en orden descendente
        history = history_collection.find().sort("timestamp", -1)
        
        historial = [
            {
                "session_id": str(doc["_id"]),  # Convertir ObjectId a string
                "query": doc.get("query", "Sin título"),
                "response": doc.get("response", ""),
                "assistance_type": doc.get("assistance_type", ""),
                "timestamp": doc.get("timestamp")
            }
            for doc in history
        ]
        return jsonify({'historial': historial})
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500