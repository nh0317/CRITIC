from urllib import response
import os, re
import openai 
from .model.model_response import get_model_response

DEFAULT_TEST_PATH ='./coverity_test/src/test/java/com/example/'
DEFAULT_SRC_PATH ='./coverity_test/src/main/java/com/example/'

def generate_unit_test(code, test_type='junit5 test', model='codellama'):
    response = get_model_response(model, code, test_type)
    # print(response)
    return paring_code(response)

def read_code(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'file not found:{file_path}')
    
    with open(file_path, 'r') as file:
        return file.read()

def _get_class_name(code):
    class_pattern = r'\bclass\s+([a-zA-Z_]\w*)'
    class_name = re.findall(class_pattern, code)[0]
    return class_name

def _save_code(file_path, code):
    with open(file_path, 'w') as file:
        file.write(code)
    
def save_src(code):
    file_path = DEFAULT_SRC_PATH+_get_class_name(code)+'.java'
    _save_code(file_path, code)
    print(f'Code saved to : {file_path}')
    
    
def save_test(test_code):
    file_path = DEFAULT_TEST_PATH+_get_class_name(test_code)+'.java'
    _save_code(file_path, test_code)
    print(f'Test Code saved to : {file_path}')

def paring_code(text):
    patterns =[r'```JAVA(.*?)```', r'```java(.*?)```', r'```(.*?)```']
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    else : return text

def main(model, test_type='Junit test'):
    print('start generating coding...')
    code_path = './data/Calculator.java'
    output_path = f'./output/generated_code_of_{model}.java'
    
    code = read_cpp_code(code_path)
    test_code = generate_unit_test(model, code, test_type)
    # print(test_code)
    save_test(output_path, test_code)

if __name__=='__main__':
    main('codellama')
