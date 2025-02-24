import json 
import urllib
import os
from pymongo import MongoClient, server_api
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
# Configuración de credenciales (considera usar variables de entorno)
username = "ornellag"
pwd = "Ornella01"

# Construcción segura de la URI
uri = f"mongodb+srv://{urllib.parse.quote_plus(username)}:{urllib.parse.quote_plus(pwd)}@cluster0.9dpllap.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Conectar a MongoDB
mongo_client = MongoClient(uri, server_api=server_api.ServerApi('1'))

try:
    mongo_client.admin.command('ping')
    print("✅ Conexión a MongoDB exitosa.")
    db = mongo_client["NW-db"]
    collection = db["json_cases"]
except Exception as e:
    print(f"❌ Error al conectarse a MongoDB: {e}")
    exit()

# Inicializar OpenAI Embeddings
openai_api_key = os.getenv("OPENAI_API_KEY")  # Usa una variable de entorno
embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Función para generar embeddings y asegurarse de que sean un array de floats
def get_embedding(text):
    try:
        response = embeddings_model.embed_query(text)
        return [float(x) for x in response]  # Convierte a lista de floats explícitamente
    except Exception as e:
        print(f"❌ Error generando embedding: {e}")
        return None  # En caso de error, retorna None

# Leer el archivo JSON
with open("C:/Users/ornella01/Desktop/NewoPruebas/project - copia/backend/Json_Cases_1.json", "r") as file:
    data = json.load(file)
   

# Limpiar la colección para evitar duplicados (opcional)
collection.delete_many({})

# Procesar e insertar documentos con embeddings
documents_to_insert = []
for doc in data:
    # Convertir los valores de causes y solutions a texto (si son diccionarios, extraer su contenido)
    # Convertir los valores de causes y solutions a texto
    causes_text = " ".join(doc.get("causes", []))  # Lista de strings, se une directamente
    solutions_text = " ".join(solution.get("description", "") for solution in doc.get("solutions", []))

    # Crear el campo `text`
    text_content = f"{doc.get('problem_type', '')} {doc.get('description', '')} {causes_text} {solutions_text}"


    # Agregar el campo `text` al documento
    doc["text"] = text_content


    # Generar embedding basado en `text`
    embedding_vector = get_embedding(text_content)

    if embedding_vector:  # Solo inserta si se generó correctamente el embedding
        doc["embedding"] = embedding_vector  # Asegura que sea un array de floats
        documents_to_insert.append(doc)

# Insertar documentos en MongoDB con manejo de errores
try:
    collection.insert_many(documents_to_insert, ordered=False)
    print("✅ Datos insertados correctamente en MongoDB con embeddings y campo 'text'.")
except Exception as e:
    print(f"❌ Error al insertar datos: {e}")

