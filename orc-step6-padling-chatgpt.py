# VERSION 5 
# NO SAVE IMG 
# NO SHOW IMG 
# PT
# USING MODEL FROM PADDLE 

from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def list_to_string(data):
    if isinstance(data, list):
        # Use recursion to flatten the list
        return ''.join(list_to_string(item) for item in data)
    else:
        # Convert non-list items to string
        return str(data)

def create_chat_completion(content):
    client.api_key = openai_api_key
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é meu assistente especializado em identificação de dados pós extração por OCR"},
            {"role": "user", "content": f"Nestes dados: {content} , por favor confira o resultada dessa extração de OCR e procure os dados mais próximos NOME: (Será o nome da pessoa). Depois procure o DOC. IDENTIDADE / ORG EMISSOR / UF. Depois o CPF, estará no formato 000.000.000-00, depois data de nascimento no formato: dd/mm/yyyy, de FILIAÇÃO, precisamos extrair o nome da mãe e o nome do pai da filiação, me retorne em JSON no formato, name:, id:, cpf:, birth_date:, father_name: e mother_name:"}
        ]
    )
    print(response.choices[0].message)
    return response.choices[0].message

def find_all_associated_texts(results, keyword, vertical_threshold=20):
    associated_texts = []
    for i, line in enumerate(results):
        text = line[1][0]
        if keyword.lower() in text.lower():
            current_coords = line[0]
            for j in range(i + 1, len(results)):
                next_text = results[j][1][0]
                next_coords = results[j][0]
                if abs(next_coords[0][1] - current_coords[0][1]) < vertical_threshold:
                    associated_texts.append(next_text)
                else:
                    break
            break
    return associated_texts

# Initialize PaddleOCR with Portuguese support and custom model
# dict_path = '/home/brpl/code/api-vision/models-pt/dict.txt'
ocr = PaddleOCR(use_angle_cls=True, lang='pt')
# ocr = PaddleOCR(use_angle_cls=True, lang='pt', rec_model_dir='/home/brpl/code/api-vision/models-pt/pt_mobile_v2.0_rec_train/pt_mobile_v2.0_rec_train')

# Path to the input image
img_path = 'orc-step6-padling-chatgpt.py'

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


# Find associated texts
name = find_all_associated_texts(results_flat, "NOME")[0] if find_all_associated_texts(results_flat, "NOME") else None
cpf = find_all_associated_texts(results_flat, "CPF")[0] if find_all_associated_texts(results_flat, "CPF") else None
rg = find_all_associated_texts(results_flat, "DOC.IDENTIDADE/ORG.EMISSOR/UF")[0] if find_all_associated_texts(results_flat, "DOC.IDENTIDADE/ORG.EMISSOR/UF") else None
parents_names = find_all_associated_texts(results_flat, "FILIACAO", vertical_threshold=70)
birth_date = find_all_associated_texts(results_flat, "DATA NASCIMENTO")[0] if find_all_associated_texts(results_flat, "DATA NASCIMENTO") else None

# Extract father's and mother's names
father_name = parents_names[0] if parents_names else None
mother_name = ' '.join(parents_names[1:]) if len(parents_names) > 1 else None

# Print categorized results
print("Categories:")
print(f"Name: {name}")
print(f"CPF: {cpf}")
print(f"RG: {rg}")
print(f"Father's Name: {father_name}")
print(f"Mother's Name: {mother_name}")
print(f"Birth Date: {birth_date}")

# OPENAI Request

result_pure_string = list_to_string(result)

chat_response = create_chat_completion(result_pure_string)
print(chat_response)

