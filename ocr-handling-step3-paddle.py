from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os

# Inicializa o PaddleOCR com suporte para português
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Caminho para a imagem de entrada
img_path = './docs/CNH.jpg'

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
# font_path = './fonts/simfang.ttf'  # Ajuste este caminho conforme necessário
im_show = draw_ocr(image, boxes, txts, scores)
im_show = Image.fromarray(im_show)

# Salva a imagem com os resultados
output_path = './docs/resultado_ocr.jpg'
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