from flask import Flask, request, jsonify
import os
import base64
import requests
import json

## API Keys
os.environ["OPENAI_API_KEY"] = ""
OPENAI_API_KEY = ""
API_KEY = ""

## Auth
def authenticate_request(req):
    api_key = req.headers.get('Authorization')
    return api_key == f"Bearer {API_KEY}"

app = Flask(__name__)

json_data = {
    "name": "",
    "cpf": "",
    "rg": "",
    "mothers_name": ""
}

json_structure = json.dumps(json_data, indent=4)

# Process Images
@app.route('/process', methods=['POST'])
def process_images():
    if not authenticate_request(request):
        return jsonify({"error": "Unauthorized"}), 401

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400

    results = []

    for file in files:
        try:
            base64_image = encode_image(file)
            response = analyze_image(base64_image)
            results.append({"file_name": file.filename, "analysis": response})
        except Exception as e:
            results.append({"file_name": file.filename, "error": str(e)})

    return jsonify(results)

def encode_image(file):
    content = file.read()
    return base64.b64encode(content).decode('utf-8')

def analyze_image(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    headers2 = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # Define the request payload
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the following information from the document: "
                                "For a driver's license: Person Name, CPF Number, RG Number, "
                                "Mother's Name, Date of Birth. "
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000,
    }


    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    final_response = response.json()['choices'][0]['message']['content']
    print("-------- FINAL RESPONSE ------------")
    print(final_response)

    new_prompt = (
        final_response + "\n" +
        "Please structure the extracted information in a strict JSON format with the following attributes:\n"
        "{\n"
        "    \"name\": \"\",\n"
        "    \"cpf\": \"\",\n"
        "    \"rg\": \"\",\n"
        "    \"date_of_birth\": \"\",\n"
        "    \"mothers_name\": \"\"\n"
        "}"
    )
    print("-------- NEW PROMPT ------------")
    print(new_prompt)
    print(type(new_prompt))
    
    # Create a new payload for the request
    new_payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Please respond with valid JSON."
            },
            {
                "role": "user",
                "content": new_prompt
            }
        ],
        "response_format": {"type": "json_object" },
        "max_tokens": 3000
    }

    # Make the request to OpenAI
    response2 = requests.post("https://api.openai.com/v1/chat/completions", headers=headers2, json=new_payload)
    print("-------- NEW RESPONSE ------------")
    
    print(response2)
    
    # if response2.status_code != 200:
    #     print(f"Error in second request: {response2.status_code} - {response2.text}")
    # return None
    # return response2.json()['choices'][0]['message']['content']
    # print("Raw response:", response2.text)

    # Check if the response was successful
    if response2.status_code == 200:
        # Parse the JSON response
        response_content = response2.json()
        
        # Debug: Print the parsed response content
        print("Parsed response content:", response_content)
        
        # Access the content which is expected to be valid JSON
        json_response = json.loads(response_content['choices'][0]['message']['content'])
        
        # Debug: Print the final JSON response
        print("Final JSON response:", json_response)
        #return response2.json()['choices'][0]['message']['content']
        return json_response
    else:
        # Handle errors
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == '__main__':
    app.run(debug=True)