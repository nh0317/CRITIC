import os
from openai import OpenAI
import ollama

def get_model_response(model, code, test_type):
    prompt = f"""
        generate a {test_type} case for the following Java code. 
        Include all necessary imports and test multiple scenarios
        the test code should meet below conditions 
        
        1. Test code should meet Test Coverage 100% 
        2. Test code should pass the {test_type}
        3. Test code should include the edge cases
        """
    messages = [{ 'role' : 'system', 'content' : prompt},
                  {'role':'user', 'content': code}]
    if model == 'gpt':
        return gpt_response(messages)
    elif model == 'llama':
        return llama_response(messages)
    elif model == 'codellama':
        return codellama_response(messages)
    else:
        print('not supported model')

def gpt_response(messages):
    api_key =os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        messages=messages,
        model='gpt-4o-mini',
        stream=False
    )
    response = response.choices[0].message.content.strip()
    return response

def llama_response(messages):
    response = ollama.chat(
        model='llama3:8b', 
        messages=messages)
    response  = response['message']['content']
    return response

def codellama_response(messages):
    response = ollama.chat(
        model='codellama:7b', 
        messages=messages)
    response  = response['message']['content']
    return response
