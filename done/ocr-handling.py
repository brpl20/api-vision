import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance
import os

def enhance_image(image_path):
    # Open the image using PIL
    img = Image.open(image_path)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Enhance brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    return np.array(img)

def process_document(image_path, output_folder):
    # Enhance the image
    img = enhance_image(image_path)
    
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    
    # Perform OCR
    result = ocr.ocr(img, cls=True)
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Draw bounding boxes and text on the image
    img_with_boxes = img.copy()
    for idx, line in enumerate(result):
        for box in line:
            points = np.array(box[0]).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(img_with_boxes, [points], True, (0, 255, 0), 2)
            cv2.putText(img_with_boxes, str(idx), tuple(points[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    
    # Save the image with bounding boxes
    output_path = os.path.join(output_folder, 'output_with_boxes.jpg')
    cv2.imwrite(output_path, cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR))
    
    # Extract and save text with layout information
    output_text = ""
    for idx, line in enumerate(result):
        for box in line:
            text = box[1][0]
            confidence = box[1][1]
            points = box[0]
            output_text += f"Box {idx}: {text} (Confidence: {confidence:.2f})\n"
            output_text += f"  Coordinates: {points}\n\n"
    
    # Save the extracted text
    text_output_path = os.path.join(output_folder, 'extracted_text.txt')
    with open(text_output_path, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    return output_path, text_output_path

def main():
    input_image = "./docs/CNH.jpg"
    output_folder = "./docs"
    
    image_output, text_output = process_document(input_image, output_folder)
    print(f"Processed image saved to: {image_output}")
    print(f"Extracted text saved to: {text_output}")

if __name__ == "__main__":
    main()