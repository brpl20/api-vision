Certainly! PaddleOCR supports Portuguese, and there are other OCR models and libraries that work well with Portuguese text. Here are some options:

1. PaddleOCR (Portuguese support):
   PaddleOCR already supports Portuguese. You can use it by changing the language parameter:

   ```python
   ocr = PaddleOCR(use_angle_cls=True, lang='pt', use_gpu=False)
   ```

2. Tesseract OCR:
   Tesseract has good support for Portuguese. You can use it with Python via the pytesseract library:

   ```python
   import pytesseract
   
   # Specify Portuguese
   text = pytesseract.image_to_string(image, lang='por')
   ```

3. EasyOCR:
   EasyOCR also supports Portuguese:

   ```python
   import easyocr
   
   reader = easyocr.Reader(['pt'])  # Initialize for Portuguese
   result = reader.readtext(image_path)
   ```

4. Google Cloud Vision API:
   While not open-source, it provides excellent OCR capabilities for Portuguese:

   ```python
   from google.cloud import vision
   
   client = vision.ImageAnnotatorClient()
   image = vision.Image(content=image_content)
   response = client.document_text_detection(image=image, image_context={"language_hints": ["pt"]})
   ```

5. Amazon Textract:
   Another cloud option with good Portuguese support, though it's a paid service.

6. BERT for Portuguese:
   While not an OCR model itself, BERT models trained on Portuguese data can be useful for post-processing OCR results to correct errors. The "neuralmind/bert-base-portuguese-cased" model on Hugging Face is a good option.

For your current setup using PaddleOCR, you can simply change the language to Portuguese like this:

```python
ocr = PaddleOCR(use_angle_cls=True, lang='pt', use_gpu=False)
```

This should work well for most Portuguese documents. If you're dealing with handwritten text or very specialized documents, you might need to look into training custom models or using more advanced techniques.

Remember that OCR accuracy can vary depending on the quality and complexity of your documents. It's often helpful to preprocess images (like we're doing with enhancement) and post-process the OCR results to improve accuracy.

If you decide to try any of these alternatives or if you need help fine-tuning the Portuguese OCR process, feel free to ask for more detailed guidance!