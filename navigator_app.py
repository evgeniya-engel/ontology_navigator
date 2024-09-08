import streamlit as st
from generator import *
import navigator

from pinecone import Pinecone, ServerlessSpec
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
import openai

# session states
if 'ontology_path' not in st.session_state:
    st.session_state['ontology_path'] ='C:\\Users\\eugen\Documents\\00_PROJECTS\\digitalbuildings'

if 'global_library' not in st.session_state:
    st.session_state['global_library'] = None

if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''

if 'pinecone_index' not in st.session_state:
    # Set up Pinecone
    pc = Pinecone(api_key='')
    # Create or connect to Pinecone Index
    index_name = "dbo-ontology-index"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536, # Replace with your model dimensions
            metric="cosine", # Replace with your model metric
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ) 
        )
    st.session_state['pinecone_index'] = pc.Index(index_name)

if 'embedding_model' not in st.session_state:
    st.session_state['embedding_model'] = None


# handlers
def execute_generator(input_implements):
    if all([st.session_state['global_library'], input_implements, st.session_state['openai_api_key']]):
        implements = get_implements(input_implements)
        type, descriptions = get_descriptions(implements, st.session_state['global_library'])
        examples = get_type_examples(type, st.session_state['global_library'])
        prompt = generate_prompt(type, descriptions, examples)
        new_type_description = get_completion_from_messages(st.session_state['openai_api_key'], prompt, temperature = 0.8)
        return new_type_description
    else:
        errors = []
        if not st.session_state['global_library']:
            errors.append("Please build obtology on Setup page first.")
        if not input_implements:
            errors.append("Enter a list of abstracts to generate description for.")
        errors_text = '\n'. join(["Unable to generate types due to following issues:"] + errors)
        return errors_text

# UI
tab_setup, tab_description_generator, tab_ontology_navigator, tab_stubby_concatenator = st.tabs(["Setup", "Generate Type Description", "Navigate Ontology", "Stubby Commands"])

with tab_setup:
    openai_api_key = st.text_input('OpenAI API Key', value=st.session_state['openai_api_key'])
    ontology_path = st.text_input('Path to Ontology', value=st.session_state['ontology_path'])
    errors = []
    if st.button("Set Up", type='primary'):
        if openai_api_key:
            st.session_state['openai_api_key'] = openai_api_key
            st.session_state['embedding_model'] = navigator.embedding_model_init(st.session_state['openai_api_key'])
        else:
            errors.append("Enter OpenAI API Key.")
        if ontology_path:
            st.session_state['ontology_path'] = ontology_path
            st.session_state['global_library'] = build_ontology_library(st.session_state['ontology_path'])
        else:    
            errors.append("Specify path to local Digital Buildings Ontology.")

        if all([st.session_state['global_library'], st.session_state['openai_api_key'], st.session_state['embedding_model']]):
            message_text = "You're all set!"
        elif len(errors) > 0:
            errors = ["Unable to generate types due to following issues:"] + errors
            message_text = '\n'. join(errors)
        else:
            message_text = "Something went wrong"

        st.text(message_text)

with tab_description_generator:
    st.title('Generate Type Description')
    input_implements = st.text_input('Insert a list of abstracts delimited by "," or a canonical type name')
    if st.button("Generate", type='primary'):
        result = execute_generator(input_implements)
    else:
        result = ""
    st.text_area('Type Description', result, height=200)

with tab_ontology_navigator:
    st.title('Navigate Ontology')
    if st.session_state['global_library'] and navigator.index_empty(st.session_state['pinecone_index'])==True:
        data = navigator.generate_data(st.session_state['global_library']['ABSTRACT'])
        documents = navigator.get_documents_from_data(data)
        docs_to_index = navigator.push_documents_to_index(documents, st.session_state['embedding_model'], st.session_state['pinecone_index'])
        if docs_to_index == True:
            st.text("Successfully built index on ABSTRACT!")
        else:
            st.text("Something went wrong.")
    
    query = st.text_area('What are you looking for?', result, height=100)

    if st.button("Search", type='primary') and query:
        query_result = navigator.semantic_search(query, st.session_state['embedding_model'], st.session_state['pinecone_index'])
        result_text = navigator.parse_query_results(query_result)
    else:
        result_text = ''

    st.text(result_text)
        

with tab_stubby_concatenator:
    st.title('Stubby Commands')