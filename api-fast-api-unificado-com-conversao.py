# Codigo Unificado
# pip install fastapi uvicorn python-multipart
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from paddleocr import PaddleOCR
from openai import OpenAI
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv

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
    # Define fields based on the questions
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

def create_chat_completion(content, prompt):
    client.api_key = openai_api_key
    response = client.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é meu assistente especializado em identificação de dados pós extração por OCR"},
            {"role": "user", "content": prompt.format(content=content)}
        ]
    )
    return response.choices[0].message['content']

def extract_text_from_file(file: UploadFile):
    # Convert file to text using OCR
    _, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        images = convert_from_path(file.file)
        text = ''.join(pytesseract.image_to_string(image) for image in images)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        image = Image.open(file.file)
        text = pytesseract.image_to_string(image)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    return text

@app.post("/process_document/", response_model=DocResponse)
async def process_document(file: UploadFile = File(...)):
    result = ocr.ocr(file.file, cls=True)
    result_pure_string = list_to_string(result)
    prompt = ("Nestes dados: {content} , por favor confira o resultada dessa extração de OCR e procure os dados mais próximos NOME: (Será o nome da pessoa). "
              "Depois procure o DOC. IDENTIDADE / ORG EMISSOR / UF. Cuidado para tentar buscar o órgão emissor e o UF do documento, eles estarão sempre a direita do número de identidade. "
              "Depois o CPF, estará no formato 000.000.000-00, depois data de nascimento no formato: dd/mm/yyyy, de FILIAÇÃO, precisamos extrair o nome da mãe e o nome do pai da filiação. "
              "O nome do pai sempre irá aparecer primeiro. O nome da mãe verticalmente abaixo, o nome da mãe pode estar dividido em duas linhas, então procure também um pouco mais abaixo. "
              "Ignore informações que não correspondam ao requerido. Se não encontrar algum dos campos volte o resultado null. A estrutura de dados deverá conter nome:, rg:, cpf:, nascimento:, nome_pai: e nome_mae:")
    chat_response = create_chat_completion(result_pure_string, prompt)
    return chat_response

@app.post("/process_bill/", response_model=BillResponse)
async def process_bill(file: UploadFile = File(...)):
    result = ocr.ocr(file.file, cls=True)
    result_pure_string = list_to_string(result)
    prompt = ("Nestes dados extraídos de uma conta de luz, água, gás ou outra conta qualquer: {content}. "
              "Por favor confira o resultado dessa extração de OCR e procure os dados mais próximos NOME: (Será o nome completo do titular da conta). "
              "Depois procure endereço. O endereço pode estar dividido em uma ou mais linhas, procure algo que faça sentido com: o nome da rua, cidade, estado e CEP. "
              "Ignore informações que não correspondam ao requerido. Se não encontrar algum dos campos volte o resultado null. A estrutura de dados deverá conter nome:, endereço:, cidade:, estado:, cep:")
    chat_response = create_chat_completion(result_pure_string, prompt)
    return chat_response

@app.post("/process_contract/", response_model=ContractResponse)
async def process_contract(file: UploadFile = File(...)):
    text_content = extract_text_from_file(file)
    prompt = ("No documento de contrato social: {content}, por favor responda as seguintes perguntas: "
              "Quem está no contrato social? Quais são as cotas e qual o valor das cotas? Quais são as principais cláusulas? "
              "Como é feito a distribuição de lucros? Quem é o sócio ou os sócios responsáveis pela operação? "
              "Qual é a atividade operacional da empresa? Qual é o endereço da Empresa? Qual é o tipo da sociedade? "
              "Há mais algum dado relevante como por exemplo é uma sociedade de advocacia? qual número de OAB? Extraia os dados dos sócios.")
    chat_response = create_chat_completion(text_content, prompt)
    return chat_response

# Run the server with: uvicorn main:app --reload

# curl -X POST "http://127.0.0.1:8000/process_document/" \
#      -H "accept: application/json" \
#      -H "Content-Type: multipart/form-data" \
#      -F "file=@your_test_image_or_pdf.jpg"


# curl -X POST "http://127.0.0.1:8000/process_bill/" \
#      -H "accept: application/json" \
#      -H "Content-Type: multipart/form-data" \
#      -F "file=@your_test_image_or_pdf.jpg"
     
# curl -X POST "http://127.0.0.1:8000/process_contract/" \
#      -H "accept: application/json" \
#      -H "Content-Type: multipart/form-data" \
#      -F "file=@your_test_contract.pdf"
