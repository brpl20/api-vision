import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from docx import Document

def extract_text_from_pdf(file_path):
    """Extract text from a PDF using OCR."""
    text = ""
    # Convert PDF to images
    images = convert_from_path(file_path)
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_image(file_path):
    """Extract text from an image using OCR."""
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text(file_path):
    """Determine file type and extract text accordingly."""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file format")

# Example usage
file_path = 'path/to/your/file.pdf'  # Change this to your file path
try:
    text_content = extract_text(file_path)
    print(text_content)
except Exception as e:
    print(f"An error occurred: {e}")