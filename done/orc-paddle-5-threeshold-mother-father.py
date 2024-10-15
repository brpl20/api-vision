# VERSION 5 
# NO SAVE IMG 
# NO SHOW IMG 
# PT
# USING MODEL FROM PADDLE 

from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os

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
img_path = './docs/CNH.jpg'

# Check if the image file exists
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image file not found: {img_path}")


# Perform OCR
result = ocr.ocr(img_path, cls=True)

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


