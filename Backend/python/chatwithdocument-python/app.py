import os
import requests
from flask import Flask, request, jsonify
import pdfplumber
import uuid
import pandas as pd
from PIL import Image
from io import BytesIO
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import torch

logging.basicConfig(level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()

# Get the MongoDB connection string from the environment variable
mongo_uri = os.getenv("MONGO_URI")
# MongoDB setup
mongo_client = MongoClient(mongo_uri)
db = mongo_client["chat_document"]
chunks_collection = db["chunks"]

# Load the tokenizer and model (assuming "google/gemini-xx" is available, replace with the actual model name)
tokenizer = AutoTokenizer.from_pretrained("google/gemini-xx")
model = AutoModel.from_pretrained("google/gemini-xx")

# Initialize Flask app
app = Flask(__name__)

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
                os.remove(local_filename)
            return jsonify({"message": "PDF processed successfully", "text": text}), 200

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

if __name__ == "__main__":
    app.run(debug=True)
