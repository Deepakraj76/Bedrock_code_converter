from flask import Flask, request, render_template
import os
import boto3
import json

app = Flask(__name__)

# Initialize the Bedrock client
bedrock = boto3.client(service_name="bedrock-runtime", region_name='ap-south-1')

def translate_code(input_code: str, target_language: str) -> str:
    if target_language == 'javascript':
        prompt = f"<s>[INST]Convert the following Python code to JavaScript:\n\n{input_code}.[/INST]"
    elif target_language == 'python':
        prompt = f"<s>[INST]Convert the following Node.js code to Python using the Flask framework:\n\n{input_code}.[/INST]"

    body = json.dumps({
        "prompt": prompt,
        "max_tokens": 1024,
        "top_p": 0.8,
        "temperature": 0.1,
    })

    modelId = "mistral.mistral-large-2402-v1:0"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock.invoke_model(
        body=body,
        modelId=modelId,
        accept=accept,
        contentType=contentType
    )

    response_body_str = response['body'].read().decode('utf-8')
    response_body = json.loads(response_body_str)
    output_text = response_body['outputs'][0]['text']

    start_index = output_text.find("```") + len("```")
    end_index = output_text.find("\n```", start_index)
    code = output_text[start_index:end_index]

    return code

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    original_code = None
    converted_code = None
    
    if request.method == 'POST':
        file = request.files['file']
        target_language = request.form['language']
        if file:
            original_code = file.read().decode('utf-8')
            converted_code = translate_code(original_code, target_language)
    
    return render_template('index.html', original_code=original_code, converted_code=converted_code)

if __name__ == "__main__":
    app.run(debug=True)
