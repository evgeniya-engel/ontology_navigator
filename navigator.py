from pinecone import Pinecone, ServerlessSpec
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
import openai

def index_empty(pinecone_index):
    query_result = pinecone_index.query(vector=[0] * 1536, top_k=1)

    if query_result['matches']:
        return False
    else:
        return True

def embedding_model_init(openai_api_key):
    # Initialize Enbedding Model
    openai.api_key = openai_api_key
    embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")  # OpenAI embedding
    return embedding_model

def generate_data(dictionary):# 
    '''
    dictionary - global dictionary
    data - list of dictionaries with keys 'description', 'metadata'
    '''
    data = []
    for key, val in dictionary.items():
        item = {
            'description': val['description'],
            'metadata': key
        }
        data.append(item)
    return data

def get_documents_from_data(data): # data - list of dictionaries with keys 'description', 'metadata'
    # Create Document objects and generate embeddings
    documents = [Document(text=doc['description'], metadata={'metadata': doc['metadata']}) for doc in data]
    return documents

def push_documents_to_index(documents, embedding_model, index):
    # Generate and store embeddings in Pinecone
    for document in documents:
        embedding = embedding_model.get_text_embedding(document.get_text())
        index.upsert(vectors=[(document.metadata['metadata'], embedding)])
    return True

# Semantic search function
def semantic_search(query: str, embedding_model, pinecone_index, num_matches=3):
    # Get query embedding
    query_embedding = embedding_model.get_text_embedding(query)
    
    # Search Pinecone for similar vectors
    query_result = pinecone_index.query(vector=query_embedding, top_k=num_matches, include_metadata=True)
    
    # Return metadata of best match
    if query_result['matches']:
        return query_result['matches']
    else:
        return None
    
def parse_query_results(matches):
    results = []
    for match in matches:
        results.append(match['id'])
    return "\n".join(results)