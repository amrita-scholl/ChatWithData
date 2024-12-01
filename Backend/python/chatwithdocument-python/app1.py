import os
import requests
import tempfile
import re
from PyPDF2 import PdfReader
import pandas as pd
from PIL import Image
from io import BytesIO

def get_filename_from_cd(cd):
    """Extract filename from Content-Disposition header."""
    if not cd:
        return None
    fname = re.findall('filename="(.+?)"', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_file(url):
    """Download a file from the given URL and return its content."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.content, response.headers.get('Content-Disposition')

def process_pdf(file_content):
    """Extract text from a PDF file."""
    reader = PdfReader(BytesIO(file_content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def process_excel(file_content):
    """Read data from an Excel file and return as a DataFrame."""
    df = pd.read_excel(BytesIO(file_content))
    return df.to_dict(orient='records')

def process_image(file_content):
    """Get basic details from an image file."""
    image = Image.open(BytesIO(file_content))
    return {
        "format": image.format,
        "size": image.size,
        "mode": image.mode
    }

def main(url):
    try:
        # Download the file from the pre-signed URL
        file_content, content_disposition = download_file(url)

        # Extract filename if available
        filename = get_filename_from_cd(content_disposition) or os.path.basename(url)

        # Remove query parameters to get the correct extension
        base_url = url.split('?')[0]
        _, ext = os.path.splitext(filename.lower())  # Get extension from filename

        if ext == '':
            ext = os.path.splitext(base_url)[1]  # Fallback to base_url if no extension in filename

        if ext == '.pdf':
            text = process_pdf(file_content)
            print(f"Extracted text from PDF: {text}")

        elif ext in ['.xls', '.xlsx']:
            data = process_excel(file_content)
            print(f"Data extracted from Excel: {data}")

        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            image_details = process_image(file_content)
            print(f"Image details: {image_details}")

        else:
            print(f"Unsupported file type: {ext}")

    except Exception as e:
        print(f"Error: {str(e)}")


# Example usage with your pre-signed URL
url = "https://chat-with-document.s3.ap-south-1.amazonaws.com/invoice2.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA3D4HYXV6WAZDYSPX%2F20241130%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20241130T102932Z&X-Amz-Expires=300&X-Amz-Signature=4f216c39e1eed03cae2f76c31d3163bf410414fa8ab5737bae686256860e85c8&X-Amz-SignedHeaders=host"
main(url)

