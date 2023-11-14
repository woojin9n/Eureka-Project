__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
import streamlit as st
import openai
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.document_loaders import JSONLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

# Set up OpenAI API Key
your_openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up directories for PDF files and metadata
pdf_directory = "./data/"
metadata_directory = "./metadata/"

# # Function to extract text from JSON data
# def extract_text_from_json(json_data):
#     # Implement based on your JSON structure
#     # For example:
#     text = json_data['chapters']  # Replace 'text_field' with the actual key
#     return text

# # Function to load JSON files from a directory
# def load_json_directory(directory_path):
#     raw_documents = []
#     for filename in os.listdir(directory_path):
#         if filename.endswith('.json'):
#             with open(os.path.join(directory_path, filename), 'r') as file:
#                 json_data = json.load(file)
#                 # Extract text from JSON data here
#                 # This depends on the structure of your JSON files
#                 text = extract_text_from_json(json_data)
#                 raw_documents.append(text)
#     return raw_documents

# Load JSON documents
for filename in os.listdir(metadata_directory):
    if filename.endswith('.json'):
        metadata_path = os.path.join(metadata_directory, filename)
        loader = JSONLoader(
            file_path=metadata_path,
            jq_schema='.chapters[]',
            text_content=True
        )
        raw_documents = loader.load()

# Split the text into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)

# Embed each chunk and load it into the vector store
db = Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key=your_openai_api_key, model='text-embeddings-ada-002'))

def get_response(prompt):
    # Function to get a response from GPT-4 using OpenAI API.
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a tax law expert AI to assist the legal profession. You provide the legal profession with the best knowledge and analyses based on the client's statement the legal profession has shared. It doesn't matter if your analysis is incomplete because it is just a reference. The legal profession will properly advise referring to your analysis as a reference. Generate response in the same language as the CLIENT ASKING."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )    
    return response['choices'][0]['message']['content']

# Function to generate embeddings using OpenAI
# def get_embeddings(text):
#     response = openai.embeddings.create(
#         model="text-embeddings-ada-002",
#         input=[text]
#     )
#     return response['data'][0]['embedding']

# Streamlit UI
st.title('ChatGPT based on Tax Law')
st.write('Type your question related to the Tax Law and get an answer.')

# Input text box for user to ask questions
user_input = st.text_input('Ask a question:')

if user_input:
    # Search in metadata
    results = db.search(user_input, num_results=1)
    if results:
        relevant_document_name = results[0]['document']['name'].replace('.json', '.pdf')
        loader = PyPDFDirectoryLoader(pdf_directory)
        pdf_data = loader.load_document(relevant_document_name)


        # TODO: Process the PDF data as needed
        
        # Get response from GPT
        reply = get_response(user_input)
        st.write('Response:', reply)
    else:
        st.write('No relevant documents found.')