from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader # para extrair direto ... 

# Load environment variables and config Paddle 
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
ocr = PaddleOCR(use_angle_cls=True, lang='pt')
basepath = "/home/brpl/od/CLEONICE RODRIGUES DA SILVA BATISTA (3171)/CNPJS"
# ctps_path = os.path.join(basepath, 'CTPS')
cnis_path = os.path.join(basepath, 'CNIS')
cnpj_path = os.path.join(basepath, 'EMPRESAS')


# def extract_text_from_ctps(directory):
#     ctps_results = {}
#     for filename in os.listdir(directory):
#         if filename.endswith('.pdf'):
#             file_path = os.path.join(directory, filename)
#             # Create a directory for each PDF
#             output_dir = os.path.join(directory, os.path.splitext(filename)[0])
#             os.makedirs(output_dir, exist_ok=True)
            
#             # Convert each PDF page to an image
#             images = convert_from_path(file_path, output_folder=output_dir, fmt='jpg')
#             document_results = {}
            
#             # Perform OCR on each image
#             for i, image in enumerate(images):
#                 image_path = os.path.join(output_dir, f'page_{i+1}.jpg')
#                 image.save(image_path, 'JPEG')
#                 result = ocr.ocr(image_path, cls=True)
#                 document_results[f'page_{i+1}.jpg'] = result
            
#             # Store the OCR results in the dictionary with the filename as the key
#             ctps_results[filename] = document_results
    
#     return ctps_results

# Define the CTPS directory path
# Extract text from all CTPS PDF files in the specified directory
# ctps = extract_text_from_ctps(ctps_path)

# Print the extracted CTPS results
# for doc_name, pages in ctps.items():
#     print(f"Results for {doc_name}:")
#     for page, data in pages.items():
#         print(f"Page: {page}")
#         for line in data:
#             print(line)


# EMPRESAS
def extract_text_from_cnpjs(directory):
    cnpjs = {}
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            # Convert PDF to images
            images = convert_from_path(file_path)
            extracted_text = ''
            # Perform OCR on each image
            for image in images:
                text = pytesseract.image_to_string(image, lang='por')
                extracted_text += text
            # Store the OCR result in the dictionary with the filename as the key
            cnpjs[filename] = extracted_text
    return cnpjs

# Extract text from all PDF files in the specified directory
cnpjs = extract_text_from_cnpjs(cnpj_path)
# print(cnpjs)
# for doc_name, data in extracted_documents.items():
#     print(f"Results for {doc_name}:")
#     print(data)

# CNIS
def extract_text_from_cnis(directory):
    cnis = {}
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            # Convert PDF to images
            images = convert_from_path(file_path)
            extracted_text = ''
            # Perform OCR on each image
            for image in images:
                text = pytesseract.image_to_string(image, lang='por')
                extracted_text += text
            # Store the OCR result in the dictionary with the filename as the key
            cnpjs[filename] = extracted_text
    return cnpjs

# Extract text from all PDF files in the specified directory
cnis = extract_text_from_cnpjs(cnis_path)


completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é meu assistente de notificações extrajudiciais."},
        {
            "role": "user",
            "content": "Você criará um arquivo .sh para gerar minhas notificações, você pode criar no formato MD que eu irei depois converter em PDF. Você vai receber uma lista de todas as empresas que cosntam no Cadastro Social (CNIS) desta pessoa que serão esses: {cnis}. Depois você irá comparar com o status endereço e e-mail das empresas que serão esses: {cnpjs}. Confira se as datas estão de acordo. Crie uma notificação identificando como Notificante a Senhora CLEONICE RODRIGUES DA SILVA BATISTA, brasileira, casada, frentista, portador do RG n ° 22.694.328-8, inscrito no CPF sob o n° 133.205.048-43, sem endereço eletrônico, residente e domiciliado na Rua Isa Maria Molinari de Morais, N° 81, Bairro Verona, Cascavel - PR, Cep: 85.819-437. Como notificado a empresa que você achou as informações. Crie um MD estruturado com vários HEADERS e uma boa formatação. ele será convertido com pandoc. Adicione o período trabalhado. Se você identificar que a empresa está inapta, baixada, ou inativa de qualquer forma, você não precisa criar o arquivo .md"
        }
    ]
)

print(completion.choices[0].message)


