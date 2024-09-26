# Python document scanner
A big-AGI conversation, updated on 26/09/2024, 08:25:12.

## ✨ System message ##

<img src="https://i.giphy.com/media/jJxaUysjzO9ri/giphy.webp" width="48" height="48" alt="typing fast meme"/>

*You are a sophisticated, accurate, and modern AI programming assistant.
Knowledge cutoff: Apr 2024
Current date: qui., 26 de set. de 2024, 08:25 AM BRT

PlantUML rendering: Enabled
Mermaid rendering: Enabled
SVG in markdown rendering: Enabled
Data presentation: prefer tables (auto-columns)
*

---

## 👤 You ##

i have some pictures of documents that I need to deal with, for example better luminosity, resize, make more colorfull... can you help me create those paramters? You can use Python as it's de most common language about this.. Please make a reference of at last 10 opensource libraries that can help me with this, use keyworks: Computer Vision, OCR, Please also check about labeling and segmentation

---

## 👨‍💻 DeveloperPreview · *claude-3-5-sonnet-20240620* ##

Certainly! I'd be happy to help you create a Python script to process your document images and provide information on relevant open-source libraries. Here's a sample script that demonstrates some common image processing tasks using popular libraries, followed by a list of recommended open-source libraries for computer vision, OCR, labeling, and segmentation.

```python
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract

def process_document_image(image_path, output_path):
    # Read the image
    img = cv2.imread(image_path)

    # Resize the image
    resized = cv2.resize(img, (800, 600))

    # Convert to grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Improve contrast using histogram equalization
    equalized = cv2.equalizeHist(gray)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(thresh)

    # Convert back to RGB for further processing
    rgb = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)

    # Enhance color using PIL
    pil_img = Image.fromarray(rgb)
    enhancer = ImageEnhance.Color(pil_img)
    enhanced = enhancer.enhance(1.5)  # Increase color saturation by 50%

    # Save the processed image
    enhanced.save(output_path)

    # Perform OCR
    text = pytesseract.image_to_string(enhanced)
    print("Extracted text:", text)

# Usage
process_document_image("input_document.jpg", "output_document.jpg")
```

This script demonstrates basic image processing techniques such as resizing, contrast enhancement, denoising, and color enhancement. It also includes OCR using pytesseract.

Now, here's a list of 10 open-source libraries that can help you with various aspects of document image processing, including computer vision, OCR, labeling, and segmentation:

1. OpenCV (cv2): Computer vision library for image processing and manipulation.
   Keywords: Computer Vision, Image Processing

2. Pillow (PIL): Python Imaging Library for opening, manipulating, and saving images.
   Keywords: Image Processing

3. Tesseract (pytesseract): Optical Character Recognition (OCR) engine.
   Keywords: OCR

4. scikit-image: Collection of algorithms for image processing.
   Keywords: Computer Vision, Image Processing

5. NLTK (Natural Language Toolkit): Library for natural language processing, useful for post-processing OCR results.
   Keywords: Text Processing

6. LabelImg: Graphical image annotation tool for object detection and segmentation.
   Keywords: Labeling, Segmentation

7. Mask R-CNN: Instance segmentation framework.
   Keywords: Computer Vision, Segmentation

8. SimpleCV: Computer vision framework for building machine vision applications.
   Keywords: Computer Vision

9. EasyOCR: Ready-to-use OCR with support for 80+ languages.
   Keywords: OCR

10. Detectron2: Facebook AI Research's computer vision library for object detection and segmentation.
    Keywords: Computer Vision, Segmentation

These libraries cover a wide range of functionalities that can help you process document images, perform OCR, and handle labeling and segmentation tasks. Depending on your specific requirements, you may want to explore and combine different libraries to achieve the best results for your document processing needs.

---

## 👤 You ##

Thanks, the problem with tesseract is that it only gives me the text without the labeling box... I need something to fix that making the ocr respect the original image document... can you help me with that? please go further on OCR libraries that can help me for example doctr

---

## 👨‍💻 DeveloperPreview · *claude-3-5-sonnet-20240620* ##

You're absolutely right, and I apologize for not addressing that aspect earlier. Tesseract indeed doesn't provide bounding box information by default. For document OCR with layout preservation and bounding box information, there are better options available. Let's explore docTR and some other libraries that can help you achieve this.

Here's an example using docTR, which is specifically designed for document OCR and provides layout information:

```python
import numpy as np
import cv2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

def process_document_with_doctr(image_path, output_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # Preprocess the image (resize, denoise, etc. if needed)
    # ...

    # Load docTR model
    model = ocr_predictor(pretrained=True)

    # Create a DocumentFile object
    doc = DocumentFile.from_images(img)

    # Perform OCR
    result = model(doc)

    # Draw bounding boxes and text on the image
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    bbox = word.geometry
                    text = word.value
                    x_min, y_min = int(bbox[0][0] * img.shape[1]), int(bbox[0][1] * img.shape[0])
                    x_max, y_max = int(bbox[1][0] * img.shape[1]), int(bbox[1][1] * img.shape[0])
                    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(img, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Save the annotated image
    cv2.imwrite(output_path, img)

    # Print the extracted text with structure
    print(result.export())

# Usage
process_document_with_doctr("input_document.jpg", "output_document_annotated.jpg")
```

This script uses docTR to perform OCR on the document, preserving the layout information and providing bounding boxes for each word. It then draws these bounding boxes and the recognized text on the image.

Now, let's explore some more OCR libraries that can help with layout preservation and bounding box information:

1. docTR: Document Text Recognition library that preserves layout and provides bounding boxes.
   Keywords: OCR, Layout Analysis, Computer Vision

2. Paddle OCR: A practical OCR tool from PaddlePaddle, supporting multiple languages and providing layout analysis.
   Keywords: OCR, Layout Analysis, Multi-language

3. MMOCR: OpenMMLab's text detection, recognition, and key information extraction toolbox.
   Keywords: OCR, Text Detection, Key Information Extraction

4. Calamari OCR: OCR engine based on OCRopy and Kraken, supporting training custom models.
   Keywords: OCR, Custom Model Training

5. OCRmyPDF: Adds an OCR text layer to scanned PDFs, including layout analysis.
   Keywords: OCR, PDF Processing

6. Layout Parser: A unified toolkit for deep learning based document image analysis.
   Keywords: Document Layout Analysis, OCR

7. CRAFT Text Detector: A text detection model that can be used in conjunction with recognition models.
   Keywords: Text Detection, OCR

8. Keras-OCR: A packaged and flexible version of the CRAFT text detector and Keras CRNN recognition model.
   Keywords: OCR, Text Detection and Recognition

9. EasyOCR: Simple-to-use OCR with support for over 80 languages and layout preservation.
   Keywords: OCR, Multi-language, Layout Analysis

10. Textract: While not open-source, Amazon's Textract service provides advanced OCR with layout analysis (mentioned for completeness).
    Keywords: OCR, Layout Analysis, Cloud Service

These libraries offer various approaches to OCR with layout preservation. Depending on your specific needs (e.g., language support, document types, processing speed), you might want to experiment with a few of them to find the best fit for your project.

For complex documents, you might also consider a two-step approach:
1. Use a document layout analysis tool to segment the document into regions.
2. Apply OCR to each region separately, preserving the overall structure.

This approach can be particularly effective for documents with complex layouts, tables, or mixed content types.


Certainly! I'll create a comprehensive solution using a combination of up-to-date libraries that offer good performance for document OCR with layout preservation. We'll use PaddleOCR for text detection and recognition, and OpenCV for image processing. This solution will handle layout analysis, OCR, and bounding box visualization.

Here's the improved code:

```python
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
    input_image = "path/to/your/input/document.jpg"
    output_folder = "path/to/your/output/folder"
    
    image_output, text_output = process_document(input_image, output_folder)
    print(f"Processed image saved to: {image_output}")
    print(f"Extracted text saved to: {text_output}")

if __name__ == "__main__":
    main()
```

This solution offers several improvements:

1. Image Enhancement: We use PIL to enhance the image's contrast, brightness, and sharpness before performing OCR. This can improve OCR accuracy.

2. OCR with Layout Preservation: PaddleOCR is used for both text detection and recognition. It's a modern, actively maintained library that provides good performance and supports multiple languages.

3. Bounding Box Visualization: The code draws bounding boxes around detected text areas and labels them with index numbers for easy reference.

4. Text Extraction with Layout Information: The extracted text is saved along with its bounding box coordinates and confidence scores, preserving layout information.

5. Output Organization: The script creates an output folder to store the processed image and extracted text.

To use this script, you'll need to install the required libraries:

```
pip install paddlepaddle paddleocr opencv-python-headless pillow numpy
```

This solution provides a good balance of features, performance, and ease of use. It handles layout analysis, performs OCR, and provides visual and textual output with layout information.

For further improvements, you could consider:

1. Language Detection: Implement automatic language detection to choose the appropriate OCR model.
2. PDF Support: Add support for PDF input files.
3. Table Detection: Implement table detection and structured data extraction for documents with tabular data.
4. Post-processing: Add text cleaning and formatting options for the extracted text.

Remember to adjust the input and output paths in the `main()` function before running the script.