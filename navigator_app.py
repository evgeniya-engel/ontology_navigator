import streamlit as st
import pandas as pd
import numpy as np
from generator import *

def execute(ontology_path, input_implements, openai_api_key):
    if all([ontology_path, input_implements, openai_api_key]):
        global_library = build_ontology_library(ontology_path)

        implements = get_implements(input_implements)
        type, descriptions = get_descriptions(implements, global_library)
        examples = get_type_examples(type, global_library)

        prompt = generate_prompt(type, descriptions, examples)

        new_type_description = get_completion_from_messages(openai_api_key, prompt, temperature = 0.8)

        return new_type_description
    else:
        errors = ["Unable to generate types due to following issues:\n"]
        if not openai_api_key:
            errors.append("Enter OpenAI API Key.")
        if not ontology_path:
            errors.append("Specify path to local Digital Buildings Ontology.")
        if not input_implements:
            errors.append("Enter a list of abstracts to generate description for.")
        errors_text = '\n'. join(errors)
        return errors_text
    
tab_description_generator, tab_ontology_navidator, tab_stubby_concatenator = st.tabs(["Generate Type Description", "Navigate Ontology", "Stubby Commands"])

with tab_description_generator:
    st.title('Generate Type Description')
    openai_api_key = st.text_input('OpenAI API Key')
    ontology_path = st.text_input('Insert link to ontology')
    input_implements = st.text_input('Insert a list of abstracts delimited by "," or a canonical type name')
    if st.button("Generate", type='primary'):
        result = execute(ontology_path, input_implements, openai_api_key)
    else:
        result = ""

    st.text_area('Type description', result, height=200)
with tab_ontology_navidator:
    st.title('Navigate Ontology')
with tab_stubby_concatenator:
    st.title('Stubby Commands')