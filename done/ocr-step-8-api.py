# API 
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

app = FastAPI()

class DocResponse(BaseModel):
    nome: str
    rg: str 
    cpf: str
    nascimento: str 
    nome_pai: str
    nome_mae: str

def list_to_string(data):
    if isinstance(data, list):
        return ''.join(list_to_string(item) for item in data)
    else:
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
    return doc_response

# Initialize PaddleOCR with Portuguese support
ocr = PaddleOCR(use_angle_cls=True, lang='pt')

@app.post("/process-document/")
async def process_document(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())

        # Perform OCR
        result = ocr.ocr(file_location, cls=True)

        # Flatten the result for easier processing
        results_flat = [line for res in result for line in res]

        # Convert OCR results to a pure string format
        result_pure_string = list_to_string(results_flat)

        # Create a chat completion
        chat_response = create_chat_completion(result_pure_string)

        return JSONResponse(content=chat_response.dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)