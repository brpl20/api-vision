from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os

# Function to find associated text
def find_associated_text(results, keyword):
    for i, line in enumerate(results):
        text = line[1][0]
        if keyword.lower() in text.lower():
            # Look for the next line within a certain vertical distance
            if i + 1 < len(results):
                next_text = results[i + 1][1][0]
                next_coords = results[i + 1][0]
                current_coords = line[0]
                # Check vertical proximity
                if abs(next_coords[0][1] - current_coords[0][1]) < 20:  # Adjust threshold as needed
                    return next_text
    return None

# Initialize PaddleOCR with Portuguese support
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Path to the input image
img_path = './docs/CNH.jpg'

# Check if the image file exists
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image file not found: {img_path}")

# Perform OCR
result = ocr.ocr(img_path, cls=True)

# Flatten the result for easier processing
results_flat = [line for res in result for line in res]

# Find associated texts
name = find_associated_text(results_flat, "NOME")
cpf = find_associated_text(results_flat, "CPF")
rg = find_associated_text(results_flat, "DOC.IDENTIDADE/ORG.EMISSOR/UF")
mothers_name = find_associated_text(results_flat, "FILIACAO")
birth_date = find_associated_text(results_flat, "DATA NASCIMENTO")


# Print categorized results
print("Categories:")
print(f"Name: {name}")
print(f"CPF: {cpf}")
print(f"RG: {rg}")
print(f"Filiação: {mothers_name}")
print(f"Birth Date: {birth_date}")

# Prepare visualization of results
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in results_flat]
txts = [line[1][0] for line in results_flat]
scores = [line[1][1] for line in results_flat]

# Draw OCR results on the image
font_path = '/home/brpl/code/api-vision/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/cmsy10.ttf'  # Adjust this path as needed

# Check if the font file exists
if not os.path.exists(font_path):
    raise FileNotFoundError(f"Font file not found: {font_path}")

# Call draw_ocr with the font path
im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
im_show = Image.fromarray(im_show)

# Save the image with OCR results
output_path = './docs/resultado_ocr.jpg'
im_show.save(output_path)

print(f"Image with OCR results saved at: {output_path}")

# Save the results to a text file
output_text = './docs/resultado_ocr.txt'
with open(output_text, 'w', encoding='utf-8') as f:
    for line in results_flat:
        f.write(f"Text: {line[1][0]}, Confidence: {line[1][1]:.4f}\n")
        f.write(f"Coordinates: {line[0]}\n\n")

print(f"OCR results saved in: {output_text}")