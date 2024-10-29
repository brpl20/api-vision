import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhance_image(image):
    logger.info("Enhancing image")
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    enhancer = ImageEnhance.Contrast(img_pil)
    img_pil = enhancer.enhance(1.5)
    
    enhancer = ImageEnhance.Brightness(img_pil)
    img_pil = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Sharpness(img_pil)
    img_pil = enhancer.enhance(1.5)
    
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def find_document_contour(image):
    height, width = image.shape[:2]
    
    # Try different thresholding methods
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # If no contours found, return the whole image
    if not contours:
        logger.warning("No contours found. Using entire image.")
        return np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype=np.float32)
    
    # Sort contours by area and keep only the largest ones (to avoid small noise)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]  # Adjust this number as needed
    
    return contours

def four_point_transform(image, pts):
    rect = np.array(pts, dtype="float32")
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def process_document(image_path, output_folder):
    logger.info(f"Processing document: {image_path}")
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")
    
    # Enhance the image
    enhanced = enhance_image(image)
    
    # Preprocess the image
    preprocessed = preprocess_image(enhanced)
    
    # Find document contours
    doc_cnts = find_document_contour(preprocessed)
    
    # Draw all contours in red (0, 0, 255 in BGR format)
    debug_img = enhanced.copy()
    cv2.drawContours(debug_img, doc_cnts, -1, (0, 0, 255), 2)  # Draw all contours in red
    
    # Save the result
    output_path = os.path.join(output_folder, 'processed_CNH.jpg')
    cv2.imwrite(output_path, debug_img)
    logger.info(f"Processed image saved to: {output_path}")

    # Save debug images
    cv2.imwrite(os.path.join(output_folder, 'enhanced.jpg'), enhanced)
    cv2.imwrite(os.path.join(output_folder, 'preprocessed.jpg'), preprocessed)
    cv2.imwrite(os.path.join(output_folder, 'contours.jpg'), debug_img)

def main():
    input_image = "./docs/doc-rg.jpg"
    output_folder = "./docs/treated"

    try:
        process_document(input_image, output_folder)
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    main()
