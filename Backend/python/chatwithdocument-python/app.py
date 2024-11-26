import os
import requests
from flask import Flask, request, jsonify
import pdfplumber
import pandas as pd
from PIL import Image
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

@app.route('/process-file', methods=['POST'])
def process_file():
    # Get the pre-signed URL from the request
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL not provided"}), 400

    # Download the file using the pre-signed URL
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch the file"}), 400

    file_content = response.content

    # Try to determine the file type and process accordingly
    try:
        # Process PDF file
        if url.lower().endswith('.pdf'):
            text = process_pdf(file_content)
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


if __name__ == "__main__":
    app.run(debug=True)
