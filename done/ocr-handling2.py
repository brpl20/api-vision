import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhance_image(image_path):
    logger.info(f"Enhancing image: {image_path}")
    try:
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        logger.info("Image enhancement completed")
        return np.array(img)
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        raise

def process_document(image_path, output_folder):
    logger.info(f"Processing document: {image_path}")
    try:
        # Enhance the image
        img = enhance_image(image_path)
        
        # Initialize PaddleOCR
        logger.info("Initializing PaddleOCR")
        ocr = PaddleOCR(use_angle_cls=True, lang='pt', use_gpu=False, show_log=False)
        
        # Perform OCR
        logger.info("Performing OCR")
        result = ocr.ocr(img, cls=True)
        
        # Check if OCR result is empty
        if not result:
            logger.warning("No text found in the image.")
            return
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Draw bounding boxes and text on the image
        logger.info("Drawing bounding boxes")
        img_with_boxes = img.copy()
        for idx, line in enumerate(result):
            for item in line:
                points = np.array(item[0]).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(img_with_boxes, [points], True, (0, 255, 0), 2)
                cv2.putText(img_with_boxes, str(idx), tuple(points[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        
        # Save the image with bounding boxes
        output_path = os.path.join(output_folder, 'output_with_boxes.jpg')
        cv2.imwrite(output_path, cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR))
        logger.info(f"Saved image with bounding boxes to: {output_path}")
        
        # Extract and save text with layout information
        logger.info("Extracting text")
        output_text = ""
        for idx, line in enumerate(result):
            for item in line:
                points, (text, confidence) = item
                output_text += f"Box {idx}: {text} (Confidence: {confidence:.2f})\n"
                output_text += f"  Coordinates: {points}\n\n"
        
        # Save the extracted text
        text_output_path = os.path.join(output_folder, 'extracted_text.txt')
        with open(text_output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        logger.info(f"Saved extracted text to: {text_output_path}")
        
        return output_path, text_output_path
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def main():
    input_image = "/LEADS-RS/test.jpg"
    output_folder = "/LEADS-RS/test-output.jpg"
    
    logger.info("Starting main function")
    try:
        image_output, text_output = process_document(input_image, output_folder)
        logger.info(f"Processed image saved to: {image_output}")
        logger.info(f"Extracted text saved to: {text_output}")
    except Exception as e:
        logger.error(f"Main function error: {str(e)}")

if __name__ == "__main__":
    main()