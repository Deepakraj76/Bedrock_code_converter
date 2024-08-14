from flask import Flask, request, render_template
import os
import boto3
import json
import autogen

app = Flask(__name__)

# Initialize the Bedrock client
bedrock = boto3.client(service_name="bedrock-runtime", region_name='ap-south-1')

def translate_code(input_code: str, target_language: str) -> str:
    if target_language == 'javascript':
        prompt = f'''<s>[INST]Transform the following Python code into JavaScript.source code={input_code} Ensure that the JavaScript code is fully functional, equivalent in logic, and optimized for modern usage. Follow these instructions:[/INST]

[INST]Module & Syntax Conversion: Replace Python modules and syntax with up-to-date JavaScript equivalents, using the latest libraries and best practices as of today’s date.[/INST]

[INST]Logical Fidelity: Accurately replicate all control structures, data handling, and functions from Python in JavaScript, ensuring the same output and behavior.[/INST]

[INST]Performance Optimization: Streamline the JavaScript code, applying performance optimizations and modern JavaScript techniques where applicable. Remove any redundant or unnecessary elements.[/INST]

[INST]Validation & Testing: Confirm that the converted JavaScript code is executable and produces the same results as the original Python code. Include basic test cases if needed.[/INST]

[INST]Output Specification: Deliver the final JavaScript code, ready for execution, with concise documentation on any key changes or optimizations made during the conversion.[/INST]'''
        
    elif target_language == 'python':
        prompt = f"""[INST]Transform the following Node.js file into a Python Flask file.source code:{input_code}. The Flask file must be fully executable and deliver the same output as the original Node.js file. Follow these instructions precisely:[/INST]

[INST]Module Replacement: Identify Node.js modules and replace them with up-to-date Python equivalents that provide identical functionality. Ensure the chosen Python modules are current as of today's date.[/INST]

[INST]Routing & Middleware: Convert Express routes and middleware to Flask-compatible routes. Maintain the original routing logic and middleware processing flow.[/INST]

[INST]Error Handling: Map Node.js error handling (try-catch and middleware error handlers) directly to Python's exception handling system, preserving custom error responses and status codes.[/INST]

[INST]Environment & Configuration: Migrate environment variables and configuration setups from Node.js (process.env) to Python’s os.environ or equivalent mechanisms, ensuring seamless integration.[/INST]

[INST]Code Optimization: Streamline the converted Python code for performance, utilizing Pythonic best practices. Remove any redundant code or unnecessary dependencies.[/INST]

[INST]Validation & Testing: Ensure the Flask file is executable, validating that its output matches the Node.js file. Implement basic test cases if necessary to confirm functional equivalence.[/INST]

[INST]Output Specification: Provide the final Flask code, ready for immediate execution, with clear documentation on any module substitutions or optimizations made.[/INST]"""

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
