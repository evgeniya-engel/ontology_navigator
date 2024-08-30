import ruamel.yaml as yaml
import openai
import random
import os

openai.api_key = ''

def build_ontology_library(ontology_path: str):
    hvac_yamls = os.listdir(ontology_path)
    global_lib = {}
    for y in hvac_yamls:
        path = resources+'\\' + y
        type = y.replace('.yaml', '')
        with open(path, 'r') as file:
            doc = yaml.load(file, Loader=yaml.RoundTripLoader)
            file.close()
        type_lib = {}
        for key, val in doc.items():
            if not isinstance(val, str):
                if type == 'ABSTRACT':
                    type_lib[key] = {'description': val.get('description')}
                else:
                    type_lib[key] = {'description': val.get('description'),
                                    'implements': val.get('implements')}
        global_lib[type] = type_lib
    return global_lib

def get_implements(input: str):
    '''
    input: a list of implements delimited by comma
    '''
    implements = input.split(",")
    implements = [i.strip() for i in implements]
    return implements
    
    
def get_descriptions(implements: list, global_library: dict):
    '''
    implements: a list of abstracts from implements
    global_library: library of descriptions built from ontology
    '''
    abstract_descriptions = []
    type = implements[0]
    for abstract in implements[1:]: # first implement is always general type, omitting
        abstract_descriptions.append(global_library['ABSTRACT'][abstract].get('description'))
    description = '. '.join(abstract_descriptions).replace("..", ".")
    return type, description

def get_type_examples(type, global_library):
    keys = list(global_library[type].keys())
    indexes = [random.randint(1, len(keys)-1) for i in range(0, 5)]
    descriptions  = [global_library[type][keys[idx]]['description'] for idx in indexes]
    return descriptions

def get_completion_from_messages(messages: list, model='gpt-3.5-turbo', temperature=0.9):
    response=openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def generate_prompt(type: str, descriptions: str, examples: list):
    example = '; '.join(examples)
    prompt = [
    {'role': 'user',
    'content': f'Combine capabilities listed in triple quotes into one consice description of a {type}. \
                Keep all descriptive details and the wording from original descriptions: """{descriptions}""". \
                Example: {example}',
    }
    ]
    return prompt


if __name__ == '__main__':

    resources = r"C:\Users\eugen\Documents\00_PROJECTS\digitalbuildings\ontology\yaml\resources\HVAC\entity_types"
    global_library = build_ontology_library(resources)

    input_implements = input("Enter a list of abstracts delimited by comma:")

    implements = get_implements(input_implements)
    type, descriptions = get_descriptions(implements, global_library)
    examples = get_type_examples(type, global_library)
    print(f"\nGenerating a type description for {type} based on capabilities: {descriptions}")

    prompt = generate_prompt(type, descriptions, examples)

    new_type_description = get_completion_from_messages(prompt, temperature = 0.8)
    print(f"\n\nType description:\n{new_type_description}")

    # C:\Users\eugen\Documents\00_PROJECTS\digitalbuildings\ontology\yaml\resources\HVAC\entity_types
    # CH, CHSWISOWM, HSWISOWM, SWTC