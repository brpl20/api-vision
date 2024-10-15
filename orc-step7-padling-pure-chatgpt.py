from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


class DocResponse(BaseModel):
    nome: str
    rg: str 
    cpf: str
    nascimento: str 
    nome_pai: str
    nome_mae: str
    #validade: str 

def list_to_string(data):
    if isinstance(data, list):
        return ''.join(list_to_string(item) for item in data)
    else:
        # Convert non-list items to string
        return str(data)

def create_chat_completion(content):
    client.api_key = openai_api_key
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é meu assistente especializado em identificação de dados pós extração por OCR"},
           {"role": "user", "content": f"Nestes dados: {content} , por favor confira o resultada dessa extração de OCR e procure os dados mais próximos NOME: (Será o nome da pessoa). Depois procure o DOC. IDENTIDADE / ORG EMISSOR / UF. Cuidado para tentar buscar o órgão emissor e o UF do documento, eles estarão sempre a direita do número de identidade. Depois o CPF, estará no formato 000.000.000-00, depois data de nascimento no formato: dd/mm/yyyy, de FILIAÇÃO, precisamos extrair o nome da mãe e o nome do pai da filiação. O nome do pai sempre irá aparecer primeiro. O nome da mãe verticalmente abaixo, o nome da mãe pode estar dividido em duas linhas, então procure também um pouco mais abaixo. Ignore informações que não correspondam ao requerido. Se não encontrar algum dos campos volte o resultado null. A estrutura de dados deverá conter nome:, rg:, cpf:, nascimento:, nome_pai: e nome_mae:"}
        ],
        response_format=DocResponse
    )
    doc_response = response.choices[0].message.parsed
    #print(response.choices[0].message)
    return response.choices[0].message


# Initialize PaddleOCR with Portuguese support and custom model
# dict_path = '/home/brpl/code/api-vision/models-pt/dict.txt'
ocr = PaddleOCR(use_angle_cls=True, lang='pt')
# ocr = PaddleOCR(use_angle_cls=True, lang='pt', rec_model_dir='/home/brpl/code/api-vision/models-pt/pt_mobile_v2.0_rec_train/pt_mobile_v2.0_rec_train')

# Path to the input image
img_path = './docs/CNH.jpg'

# Check if the image file exists
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image file not found: {img_path}")


# Perform OCR
result = ocr.ocr(img_path, cls=True)
print(type(result))

# Flatten the result for easier processing
results_flat = [line for res in result for line in res]
print("OCR Results:")
for line in results_flat:
   print(f"Text: {line[1][0]}, Confidence: {line[1][1]:.4f}, Coordinates: {line[0]}")

# OPENAI Request

result_pure_string = list_to_string(result)

chat_response = create_chat_completion(result_pure_string)
print(chat_response)