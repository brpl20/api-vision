from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os

# Inicializa o PaddleOCR com suporte para português
ocr = PaddleOCR(use_angle_cls=True, lang='en')


# Function to find associated text
def find_all_associated_texts(results, keyword, vertical_threshold=30):
    associated_texts = []
    for i, line in enumerate(results):
        text = line[1][0]
        if keyword.lower() in text.lower():
            # Look for subsequent lines within a certain vertical distance
            for j in range(i + 1, len(results)):
                next_text = results[j][1][0]
                next_coords = results[j][0]
                current_coords = line[0]
                # Check vertical proximity with a wider threshold
                if abs(next_coords[0][1] - current_coords[0][1]) < vertical_threshold:
                    associated_texts.append(next_text)
                else:
                    break
    return associated_texts




# Caminho para a imagem de entrada
img_path = './LEADS-RS/lawyer_image_AlbertoDiesel.jpg'
# Flatten the result for easier processing
result = ocr.ocr(img_path, cls=True)
results_flat = [line for res in result for line in res]


# Verifica se o arquivo de imagem existe
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image file not found: {img_path}")

# Realiza o OCR
result = ocr.ocr(img_path, cls=True)

# Imprime os resultados
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

# Prepara a visualização dos resultados
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result[0]]
txts = [line[1][0] for line in result[0]]
scores = [line[1][1] for line in result[0]]

# Desenha os resultados na imagem
# Nota: Você pode precisar especificar um caminho de fonte válido
font_path = '/home/brpl/code/api-vision/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/cmsy10.ttf'  # Ajuste este caminho conforme necessário

# Verifica se o arquivo de fonte existe
if not os.path.exists(font_path):
    raise FileNotFoundError(f"Font file not found: {font_path}")

# Chama a função draw_ocr com o caminho da fonte
im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
im_show = Image.fromarray(im_show)


# Singular
# telefone = find_associated_text(results_flat, "Telefone Profissional")
# print(f"Telefone: {telefone}")

# Plural
# Use the modified function to find all associated phone numbers
telefone_list = find_all_associated_texts(results_flat, "Telefone Profissional", vertical_threshold=50)
print("Telefones:", ", ".join(telefone_list))


# Salva a imagem com os resultados
output_path = './LEADS-RS/test-resultado.jpg'
im_show.save(output_path)

print(f"Imagem com resultados do OCR salva em: {output_path}")

# Salva os resultados em um arquivo de texto
output_text = './docs/resultado_ocr.txt'
with open(output_text, 'w', encoding='utf-8') as f:
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            f.write(f"Texto: {line[1][0]}, Confiança: {line[1][1]:.4f}\n")
            f.write(f"Coordenadas: {line[0]}\n\n")

print(f"Resultados do OCR salvos em: {output_text}")