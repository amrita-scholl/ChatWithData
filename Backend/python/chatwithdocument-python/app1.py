import openai
import logging
import os
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from flask_cors import CORS



load_dotenv()

app = Flask(__name__)

CORS(app)  # This will allow all domains, or you can specify allowed origins.

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get the MongoDB connection string from the environment variable
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup
mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = mongo_client["chat_document"]
chunks_collection = db["chunks"]

# Function to get chunks from MongoDB by doc_id
def get_chunks_by_doc_id(doc_id):
    # Query MongoDB to find chunks related to the doc_id
    chunks = chunks_collection.find({"doc_id": doc_id})  # Search for chunks by doc_id
    texts = [chunk["text"] for chunk in chunks if "text" in chunk]
    logger.info(f"Retrieved chunks for doc_id {doc_id}: {texts[:5]}...")  # Log a portion of the chunks for debugging
    return texts

# Function to generate response from OpenAI using doc_id
def generate_response(doc_id, query):
    chunks = get_chunks_by_doc_id(doc_id)  # Fetch chunks related to the document
    if not chunks:
        return "No content found for this document. Please check the doc_id."

    context = " ".join(chunks)  # Combine all chunks as context for the response
    combined_input = context + "\n\n" + query  # Add the user query to the context
    
    # Use the correct endpoint for chat models (v1/chat/completions)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate chat model (e.g., "gpt-3.5-turbo")
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_input}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

# Route to handle chat request
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()  # Get the JSON data from the request body
    logger.info(data)
    if not data or "doc_id" not in data or "query" not in data:
        return jsonify({"error": "doc_id and query must be provided"}), 400

    doc_id = data["doc_id"]
    query = data["query"]
    response = generate_response(doc_id, query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
