__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
import streamlit as st
import openai
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Set up OpenAI API Key
your_openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up directories for PDF files and metadata
pdf_directory = "./data/"
metadata_directory = "./metadata/"

class Document:
    def __init__(self, name, page_content, metadata=None):
        self.name = name
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}

# Load Metadata
metadata_documents = []
for filename in os.listdir(metadata_directory):
    if filename.endswith('.json'):
        with open(os.path.join(metadata_directory, filename), 'r') as f:
            doc_data = json.load(f)
            # Use filename or any other relevant information as metadata
            document = Document(name=filename, page_content=json.dumps(doc_data), metadata={"filename": filename})
            metadata_documents.append(document)

# Embed metadata and load it into the vector store
db = Chroma.from_documents(metadata_documents, OpenAIEmbeddings(openai_api_key=your_openai_api_key))

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
def get_embeddings(text):
    response = openai.embeddings.create(
        model="text-embeddings-ada-002",
        input=[text]
    )
    return response['data'][0]['embedding']

# Streamlit UI
st.title('ChatGPT based on Tax Law')
st.write('Type your question related to the Tax Law and get an answer.')

# Input text box for user to ask questions
user_input = st.text_input('Ask a question:')

if user_input:
    # Generate embeddings for the user's query
    query_embeddings = get_embeddings(user_input)

    # Search in the Chroma database using embeddings
    results = db.search_by_embedding(query_embeddings, num_results=1)
    if results:
        relevant_document_name = results[0]['document']['name'].replace('.json', '.pdf')
        loader = PyPDFDirectoryLoader(pdf_directory)
        pdf_data = loader.load_document(relevant_document_name)
        
        # Process the PDF data
        if isinstance(pdf_data, dict) and 'text' in pdf_data:
            pdf_content_json = pdf_data['text']
            try:
                pdf_content = json.loads(pdf_content_json)
                # TODO: Further process or display pdf_content as needed
            except json.JSONDecodeError:
                st.write("Error decoding PDF content from JSON.")
        
        # Get response from GPT
        reply = get_response(user_input)
        st.write('Response:', reply)
    else:
        st.write('No relevant documents found.')