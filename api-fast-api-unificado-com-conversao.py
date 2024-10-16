# Codigo Unificado
# pip install fastapi uvicorn python-multipart pillow numpy
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from paddleocr import PaddleOCR
from openai import OpenAI
import os
import pytesseract
import tempfile
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
import numpy as np
from io import BytesIO
import cv2

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Initialize FastAPI
app = FastAPI()

# Initialize PaddleOCR with Portuguese support
ocr = PaddleOCR(use_angle_cls=True, lang='pt')

# Define the response models
class DocResponse(BaseModel):
    nome: str
    rg: str 
    cpf: str
    nascimento: str 
    nome_pai: str
    nome_mae: str

class BillResponse(BaseModel):
    nome: str
    endereço: str 
    cidade: str
    estado: str 
    cep: str

class ContractResponse(BaseModel):
    socios: str
    cotas: str
    clausulas: str
    distribuicao_lucros: str
    responsaveis: str
    atividade_operacional: str
    endereco: str
    tipo_sociedade: str
    dados_relevantes: str
    socios_detalhes: str

def list_to_string(data):
    if isinstance(data, list):
        return ''.join(list_to_string(item) for item in data)
    else:
        return str(data)

def create_chat_completion(content, prompt, ai_model, response_format):
    client.api_key = openai_api_key
    response = client.beta.chat.completions.parse(
        model=ai_model,
        messages=[
            {"role": "system", "content": "Você é meu assistente especializado em identificação de dados pós extração por OCR tendo como referência as coordenadas indicadas pela extração via OCR para se localizar na estrutura do documento. Imagine sempre que você está trabalhando com um documento."},
            {"role": "user", "content": prompt.format(content=content)}
        ],
        response_format=response_format
    )
    return response.choices[0].message.parsed


def extract_text_from_file(file: UploadFile):
    _, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        # Save the file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
        
        try:
            images = convert_from_path(temp_file_path)
            text = ''.join(pytesseract.image_to_string(image) for image in images)
        finally:
            os.remove(temp_file_path)  # Clean up the temporary file
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        image = Image.open(file.file)
        text = pytesseract.image_to_string(image)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    return text

def preprocess_image_to_gray_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def convert_pdf_to_images(file: UploadFile, max_pages: int = 2):
    _, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()

    # Read the file content into memory
    file_content = file.file.read()

    if file_extension == '.pdf':
        # Save the PDF to a temporary file and convert it to images
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            images = convert_from_path(temp_file_path, first_page=1, last_page=max_pages)
        finally:
            os.remove(temp_file_path)  # Clean up the temporary file
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # Process image files directly
        images = [Image.open(BytesIO(file_content))]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    return images


@app.post("/process_bill/", response_model=BillResponse)
async def process_bill(file: UploadFile = File(...)):
    images = convert_pdf_to_images(file)
    result_strings = []

    for image in images:
        img_array = np.array(image)
        result = ocr.ocr(img_array, cls=True)
        print(result)
        result_strings.append(list_to_string(result))
    
    result_pure_string = ''.join(result_strings)
    prompt = ("Nestes dados extraídos de uma conta de luz, água, gás ou outra conta qualquer: {content}. "
              "Por favor confira o resultado dessa extração de OCR e procure os dados mais próximos NOME: (Será o nome completo do titular da conta). Se houver mais de um endereço seja restrito em pegar os mais proximos ao nome sem exceção. Exclua os demais"
              "Se for uma conta de água da SANEPAR, por favor exclua o endereço com o CEP 80.215-900 e considere apenas o segundo endereço. Que estará próximo do texto LOCAL"
              "Primeiro identifique a empresa e seu endereço, deve ser o primeiro endereço que você encontrar, geralmente eles estarão no topo do documento ou no rodapé. Use as marcações do OCR para identificar isso"
              "Não confunda o endereço da companhia de luz, água, gás ou outra qualquer com o endereço do cliente. O endereço do cliente sempre vai estar mais próximo do seu nome do que dos outros elementos do documento."
              "Depois procure endereço do cliente. O endereço pode estar dividido em uma ou mais linhas, procure algo que faça sentido com: o nome da rua, cidade, estado e CEP."
              "Ignore informações que não correspondam ao requerido. Se não encontrar algum dos campos volte o resultado null. A estrutura de dados deverá conter nome:, endereço:, cidade:, estado:, cep:")
    chat_response = create_chat_completion(result_pure_string, prompt, "gpt-4o-mini", BillResponse)
    return chat_response

@app.post("/process_document/", response_model=DocResponse)
async def process_documents(file: UploadFile = File(...)):
    images = convert_pdf_to_images(file)
    result_strings = []

    for image in images:
        img_array = np.array(image)
        result = ocr.ocr(img_array, cls=True)
        print(result)
        result_strings.append(list_to_string(result))
    
    result_pure_string = ''.join(result_strings)
    prompt = ("Nestes dados: {content} , por favor confira o resultada dessa extração de OCR e procure os dados mais próximos NOME: ou NOME Será o nome da pessoa)."
              "Depois procure o DOC. IDENTIDADE / ORG EMISSOR / UF. Cuidado para tentar buscar o órgão emissor e o UF do documento, eles estarão sempre a direita do número de identidade. "
              "Depois o CPF, estará no formato 000.000.000-00, depois data de nascimento no formato: dd/mm/yyyy, de FILIAÇÃO, precisamos extrair o nome da mãe e o nome do pai da filiação. "
              "O nome do pai sempre irá aparecer primeiro. O nome da mãe verticalmente abaixo, o nome da mãe pode estar dividido em duas linhas, então procure também um pouco mais abaixo. "
              "Ignore informações que não correspondam ao requerido. Se não encontrar algum dos campos volte o resultado null. A estrutura de dados deverá conter nome:, rg:, cpf:, nascimento:, nome_pai: e nome_mae:")
    chat_response = create_chat_completion(result_pure_string, prompt, "gpt-4o-mini", DocResponse)
    return chat_response

@app.post("/process_contract/", response_model=ContractResponse)
async def process_contract(file: UploadFile = File(...)):
    text_content = extract_text_from_file(file)
    prompt = ("No documento de contrato social: {content}, por favor responda as seguintes perguntas: "
              "Quem está no contrato social? Quais são as cotas e qual o valor das cotas? Quais são as principais cláusulas? "
              "Como é feito a distribuição de lucros? Quem é o sócio ou os sócios responsáveis pela operação? "
              "Qual é a atividade operacional da empresa? Qual é o endereço da Empresa? Qual é o tipo da sociedade? "
              "Há mais algum dado relevante como por exemplo é uma sociedade de advocacia? qual número de OAB? Extraia os dados dos sócios.")
    chat_response = create_chat_completion(text_content, prompt, "gpt-4o-mini", ContractResponse)
    return chat_response