from paddleocr import PaddleOCR
import os
import csv
import re

# Initialize PaddleOCR with support for English
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Function to find associated texts
def find_all_associated_texts(results, keyword, vertical_threshold=30):
    associated_texts = []
    for i, line in enumerate(results):
        text = line[1][0]
        if keyword.lower() in text.lower():
            for j in range(i + 1, len(results)):
                next_text = results[j][1][0]
                next_coords = results[j][0]
                current_coords = line[0]
                if abs(next_coords[0][1] - current_coords[0][1]) < vertical_threshold:
                    associated_texts.append(next_text)
                else:
                    break
    return associated_texts

# Function to extract lawyer's name from filename
def extract_lawyer_name(filename):
    match = re.search(r'lawyer_image_(.+)\.jpg', filename)
    if match:
        return match.group(1)
    return None

# Folder containing the images
folder_path = './LEADS-RS/'

# Prepare CSV file
csv_file_path = './lawyers_data.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['lawyers_name', 'phone1', 'phone2'])

    # Process each image in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            
            # Extract lawyer's name from filename
            lawyer_name = extract_lawyer_name(filename)
            
            # Perform OCR
            result = ocr.ocr(img_path, cls=True)
            results_flat = [line for res in result for line in res]

            # Find phone numbers
            phone_list = find_all_associated_texts(results_flat, "Telefone Profissional", vertical_threshold=50)

            # Prepare data for CSV
            phone1 = phone_list[0] if len(phone_list) > 0 else ''
            phone2 = phone_list[1] if len(phone_list) > 1 else ''

            # Write to CSV
            csv_writer.writerow([lawyer_name, phone1, phone2])

            print(f"Processed: {filename}")

print(f"Results saved to: {csv_file_path}")