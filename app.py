__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
import streamlit as st
from openai import OpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

# Set up OpenAI API Key
my_openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up PDF files and metadata loading
pdf_directory = "./data/"
loader = PyPDFDirectoryLoader(pdf_directory)
raw_documents = loader.load()

# Load Metadata
metadata = {}
for filename in os.listdir(pdf_directory):
    if filename.endswith('.json'):
        with open(os.path.join(pdf_directory, filename), 'r') as f:
            file_key = filename.replace('.json', '.pdf')
            metadata[file_key] = json.load(f)

# Text Splitter
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# Process documents and attach metadata
documents = []
for doc in raw_documents:
    doc_metadata = metadata.get(doc['name'])
    chunks = text_splitter.split_text(doc['text'])
    for chunk in chunks:
        chunk['metadata'] = doc_metadata
        documents.append(chunk)

# Embed each chunk and load it into the Chroma database
db = Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key=my_openai_api_key))

# ... Rest of the Streamlit and OpenAI API code ...


def get_response(prompt):
    """Function to get a response from GPT-4 using OpenAI API."""
    client = OpenAI(api_key=my_openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a tax law expert AI to assist the legal profession. You provide the legal profession with the best knowledge and analyses based on the client's statement the legal profession has shared. It doesn't matter if your analysis is incomplete because it is just a reference. The legal profession will properly advise referring to your analysis as a reference. Generate response in the same language as the CLIENT ASKING."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )    
    return response

# Streamlit UI
st.title('ChatGPT based on Tax Law')
st.write('Type your question related to the Tax Law and get an answer.')

# Input text box for user to ask questions
user_input = st.text_input('Ask a question:')

if user_input:
    # TODO: You might want to preprocess or append context from your vector store
    # to the user input before passing to the GPT model.
    
    reply = get_response(user_input)
    st.write('Response:', reply)
