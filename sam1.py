import torch
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamPredictor

# Carregar o modelo SAM
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
sam = sam_model_registry["vit_h"](checkpoint="/home/brpl/DOWNLOADS/sam_vit_h_4b8939.pth")
sam.to(device=device)

# Carregar a imagem
image_path = "./docs/CNH.jpg"
image = Image.open(image_path)
image_np = np.array(image)

# Inicializar o preditor SAM
predictor = SamPredictor(sam)
predictor.set_image(image_np)

# Segmentar um objeto na imagem
# Aqui, estamos usando um ponto de exemplo. Você pode ajustar conforme necessário.
input_point = np.array([[100, 200]])  # Coordenadas (x, y) do ponto
input_label = np.array([1])  # 1 para foreground, 0 para background

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True
)

# Visualizar o resultado
plt.figure(figsize=(10, 10))
plt.imshow(image_np)
for mask in masks:
    plt.imshow(mask, alpha=0.5)  # Ajuste a transparência conforme necessário
plt.axis('off')
plt.show()