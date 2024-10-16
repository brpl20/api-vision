from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os
import pdb
import openai
import base64
import requests

## API Keys
os.environ["OPENAI_API_KEY"] = "ENV"
OPENAI_API_KEY = "ENV"

API_KEY = "ENV"

## Auth
def authenticate_request(req):
    api_key = req.headers.get('Authorization')
    return api_key == f"Bearer {API_KEY}"

## WF Family
documents = SimpleDirectoryReader("/home/adv5898/mysite/datawffamily/").load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist()
PERSIST_DIR = "/home/adv5898/mysite/datawffamily/.storage"

## WF Financeiro
documents_fin = SimpleDirectoryReader("/home/adv5898/mysite/wffin/").load_data()
index_fin = VectorStoreIndex.from_documents(documents)
index_fin.storage_context.persist()
PERSIST_DIR_FIN = "/home/adv5898/mysite/wffin/.storage"

app = Flask(__name__)

#@app.route('/')
#def hello_world():
#    return 'Hello from Flask!'

## WF Family Route
@app.route('/chat', methods=['POST'])
#@authenticate
def chat():
    input_string = request.json['input_string']
    documents = SimpleDirectoryReader("/home/adv5898/mysite/datawffamily/").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()
    PERSIST_DIR = "/home/adv5898/mysite/datawffamily/.storage"


    # Get the input string from the request
    query_engine = index.as_query_engine()
    query_ask = query_engine.query(input_string)
    return query_ask.response


## WF Fin Route
@app.route('/chatfin', methods=['POST'])
#@authenticate
def chatfin():
    input_string = request.json['input_string']
    documents_fin = SimpleDirectoryReader("/home/adv5898/mysite/wffin/").load_data()
    index_fin = VectorStoreIndex.from_documents(documents_fin)
    index_fin.storage_context.persist()
    PERSIST_DIR_FIN = "/home/adv5898/mysite/wffin/.storage"


    # Get the input string from the request
    query_engine_fin = index_fin.as_query_engine()
    query_ask_fin = query_engine_fin.query(input_string)
    return query_ask_fin.response

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
                                "For an address bill: Street, Number, CEP, Account Holder."
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
        "max_tokens": 3000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']







