from flask import Flask, request, render_template
import os
import boto3
import json
from autogen import ConversableAgent  # Ensure correct import based on your environment

app = Flask(__name__)

# Initialize the Bedrock client
bedrock = boto3.client(service_name="bedrock-runtime", region_name='ap-south-1')

# Initialize the code writer agent with Google Gemini
code_writer_system_message = """You are a helpful AI assistant...
# (include the full system message as needed)...
"""
code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config={"config_list": [{"model": "gemini", "api_key": "AIzaSyC8G-bZEY3a1QRkL_c0g1bQlcnGWWG_--U"}]},
    code_execution_config=False,  # Turn off code execution for this agent.
)

def translate_code(input_code: str, target_language: str) -> str:
    if target_language == 'javascript':
        prompt = f"<s>[INST]Convert the following Python code to JavaScript:\n\n{input_code}.[/INST]"
    elif target_language == 'python':
        prompt = f'''[INST]Convert the following Node.js code to Python using the Flask framework:\n\n{input_code}.[/INST]
        [INST]make the code on the python and import all the required modules on the python[/INST]'''

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

def execute_code(code: str) -> str:
    # Define the conversation prompt for code execution
    execution_prompt = f"[INST]Execute the following code:\n\n{code}.\n[INST]"

    try:
        # Start a conversation with the agent
        conversation = code_writer_agent.start_conversation(execution_prompt)

        # Check if conversation is a string, dict, or custom object
        if isinstance(conversation, dict):
            result = conversation.get("text", "No response text found.")
        elif hasattr(conversation, "get_latest_response"):
            result = conversation.get_latest_response().get("text", "No response text found.")
        else:
            result = str(conversation)  # Ensure it's a string if it isn't already
    except AttributeError as e:
        result = f"AttributeError encountered: {str(e)}"
    
    # Extract and format the conversation
    conversation_text = f"User: {execution_prompt}\nAgent: {result}"

    return conversation_text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    original_code = None
    converted_code = None
    conversation_log = None
    
    if request.method == 'POST':
        file = request.files['file']
        target_language = request.form['language']
        execute_flag = 'execute' in request.form  # Checkbox or button to trigger execution
        if file:
            original_code = file.read().decode('utf-8')
            converted_code = translate_code(original_code, target_language)
            if execute_flag:
                conversation_log = execute_code(converted_code)
    
    return render_template('index2.html', original_code=original_code, converted_code=converted_code, conversation_log=conversation_log)

if __name__ == "__main__":
    app.run(debug=True)
