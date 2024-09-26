from PIL import Image, ImageEnhance
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhance_image(image_path):
    logger.info(f"Attempting to enhance image: {image_path}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Open the image
        img = Image.open(image_path)
        logger.info(f"Image opened successfully. Size: {img.size}, Mode: {img.mode}")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        logger.info("Contrast enhancement applied")

        # Enhance brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        logger.info("Brightness enhancement applied")

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        logger.info("Sharpness enhancement applied")

        # Convert to numpy array
        img_array = np.array(img)
        logger.info(f"Converted to numpy array. Shape: {img_array.shape}")

        return img_array
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        raise

def main():
    input_image = "./docs/CNH.jpg"
    output_image = "./docs/enhanced_CNH.jpg"

    logger.info("Starting image enhancement process")
    try:
        enhanced_img = enhance_image(input_image)
        
        # Save the enhanced image
        Image.fromarray(enhanced_img).save(output_image)
        logger.info(f"Enhanced image saved to: {output_image}")
    except Exception as e:
        logger.error(f"Main function error: {str(e)}")

if __name__ == "__main__":
    main()