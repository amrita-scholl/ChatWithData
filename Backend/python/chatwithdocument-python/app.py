import os
import requests
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from pydantic import BaseModel
import pdfplumber
import uuid
import pandas as pd
from PIL import Image
from typing import List
from io import BytesIO
import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from transformers import BertTokenizer, BertModel
from google.cloud import aiplatform
from flask_cors import CORS
import openai



logging.basicConfig(level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()

# Get the MongoDB connection string from the environment variable
mongo_uri = os.getenv("MONGO_URI")
# MongoDB setup
mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = mongo_client["chat_document"]
chunks_collection = db["chunks"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# PROJECT_ID = "tokyo-mark-373502"
# LOCATION = "us-central1"
# MODEL_NAME = "gemini-1.5-pro"  # Replace with "gemini-1.5-pro" if applicable

# # Load the tokenizer and model (assuming "google/gemini-xx" is available, replace with the actual model name)
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModel.from_pretrained(MODEL_NAME)
# Initialize Vertex AI
# aiplatform.init(project=PROJECT_ID, location=LOCATION)

# # Load the model
# model = aiplatform.generation_ai.TextGenerationModel(model_name=MODEL_NAME)

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Initialize Flask app
app = Flask(__name__)

CORS(app)  # This will allow all domains, or you can specify allowed origins.


@app.route('/process-file', methods=['POST'])
def process_file():

    print(f"File downloaded successfully and saved as {request}")

    class ChunkEmbedding(BaseModel):
        chunk_id: str
        text: str
        embedding: List[float]
        doc_id: str
    local_filename = 'downloaded_file.pdf'

    # Get the pre-signed URL from the request
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL not provided"}), 400


    logging.info(f"URL: {url}")
    # Download the file using the pre-signed URL
    response = requests.get(url)
    
    # Open a local file to write the content
    download_file_from_presigned_url(url, local_filename)

    print(f"File downloaded successfully and saved as {local_filename}")

    file_content = response.content

    # Try to determine the file type and process accordingly
    try:
        doc_id = str(uuid.uuid4())
        chunk_size: int = 512
        chunk_ids = []
        # Process PDF file
        #if url.lower().endswith('.pdf'):
        if '.pdf' in url.lower():
            # Extract text from PDF
            text = extract_text_from_pdf(file_path=local_filename)
            logging.info("Extracted text from PDF")
            #text = process_pdf(file_content)
            # Break text into chunks
            chunks = break_text_into_chunks(text, chunk_size)
            logging.info(f"Text broken into {len(chunks)} chunks")
            # Insert chunks and embeddings into MongoDB
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                chunk_ids.append(chunk_id)
                embedding = get_embeddings(chunk)
                chunk_embedding = ChunkEmbedding(chunk_id=chunk_id, text=chunk, embedding=embedding, doc_id=doc_id)
                chunks_collection.insert_one(chunk_embedding.dict())
                logging.info(f"Inserted chunk {chunk_id} into MongoDB")

                # Clean up temporary file
                #os.remove(local_filename)
            return jsonify({"message": "PDF processed successfully", "doc_id": doc_id}), 200

        # Process Excel file
        elif url.lower().endswith('.xls') or url.lower().endswith('.xlsx'):
            df = process_excel(file_content)
            return jsonify({"message": "Excel processed successfully", "data": df.to_dict(orient='records')}), 200

        # Process image file
        elif url.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_details = process_image(file_content)
            return jsonify({"message": "Image processed successfully", "details": image_details}), 200

        else:
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def download_file_from_presigned_url(url, destination):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully to {destination}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def process_pdf(file_content):
    """Process the PDF file and extract text."""
    text = ""
    try:
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text()  # Extract text from each page
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
    return text


def process_excel(file_content):
    """Process Excel file and return the data as a dataframe."""
    try:
        df = pd.read_excel(BytesIO(file_content))
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")
    return df


def process_image(file_content):
    """Process image and return basic image details (size, format)."""
    try:
        image = Image.open(BytesIO(file_content))
        image_details = {
            "format": image.format,
            "size": image.size,
            "mode": image.mode
        }
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
    return image_details

# Utility function to extract text from a PDF file
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    pdf_document = fitz.open(file_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Utility function to break text into chunks
def break_text_into_chunks(text: str, chunk_size: int = 512) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def uuid4():
    """Generate a random UUID."""
    return UUID(bytes=os.urandom(16), version=4)

# Utility function to create embeddings
def get_embeddings(text: str):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).flatten().tolist()
    return embeddings

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
