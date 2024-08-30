import streamlit as st
import pandas as pd
import numpy as np
from generator import *

openai.api_key = ''
def execute(resources, input_implements):
    global_library = build_ontology_library(resources)

    implements = get_implements(input_implements)
    type, descriptions = get_descriptions(implements, global_library)
    examples = get_type_examples(type, global_library)

    prompt = generate_prompt(type, descriptions, examples)

    new_type_description = get_completion_from_messages(prompt, temperature = 0.8)

    st.text_area('Type description', new_type_description)


st.title('Ontology Type Generator')
resources = st.text_input('Insert link to ontology')
input_implements = st.text_input('Insert a list of abstractsa delimited by ","')
st.button("Generate", type='primary', on_click=execute(resources, input_implements))
