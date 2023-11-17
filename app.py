__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
import streamlit as st
import openai
import PyPDF2
import chromadb
# from langchain.document_loaders import PyPDFDirectoryLoader
# from langchain.document_loaders import JSONLoader
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores import Chroma

# Set up OpenAI API Key
your_openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = your_openai_api_key

# Set up directories for PDF files and metadata
pdf_directory = "./data/"
metadata_directory = "./metadata/"

# Custom text splitter function
def custom_text_splitter(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# def custom_text_splitter(text, chunk_size=1000):
#     return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

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

# def load_and_process_json(files, jq_schema, text_splitter):
#     documents = []
#     for file_path in files:
#         loader = JSONLoader(file_path=file_path, jq_schema=jq_schema, text_content=False)
#         raw_documents = loader.load()
#         documents.extend(text_splitter.split_documents(raw_documents))
#     return documents

# def load_metadata(directory):
#     metadata = {}
#     for filename in os.listdir(directory):
#         if filename.endswith('.json'):
#             file_path = os.path.join(directory, filename)
#             with open(file_path, 'r') as file:
#                 # Assuming the metadata JSON file name corresponds to the PDF file name
#                 pdf_filename = filename.replace('.json', '.pdf')
#                 metadata[pdf_filename] = json.load(file)
#     return metadata

# def load_and_process_pdf(directory, metadata, file_extension, chunk_size=1000):
#     documents = []
#     for filename in os.listdir(directory):
#         if filename.endswith(file_extension):
#             file_path = os.path.join(directory, filename)
            
#             # Retrieve corresponding metadata for the PDF
#             pdf_metadata = metadata.get(filename, {})

#             with open(file_path, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 raw_text = ''
#                 for page in pdf_reader.pages:
#                     raw_text += page.extract_text() + ' '

#                 # Split the text into chunks using the custom text splitter
#                 chunks = custom_text_splitter(raw_text, chunk_size)

#                 # Combine each chunk with its metadata
#                 for chunk in chunks:
#                     formatted_document = {
#                         'content': chunk,  # The chunk of text
#                         'metadata': pdf_metadata  # The corresponding metadata
#                     }
#                     documents.append(formatted_document)
#     return documents

# def format_for_chroma(documents):
#     formatted_documents = []
#     for doc in documents:
#         formatted_doc = {
#             'page_content': doc['content'],  # Ensure 'content' is the correct key
#         }
#         formatted_documents.append(formatted_doc)
#     return formatted_documents

# # Load JSON documents
# for filename in os.listdir(metadata_directory):
#     if filename.endswith('.json'):
#         metadata_path = os.path.join(metadata_directory, filename)
#         loader = JSONLoader(
#             file_path=metadata_path,
#             jq_schema='.chapters[]',
#             text_content=False
#         )
#         raw_documents = loader.load()

# Split the text into chunks
# documents = text_splitter.split_documents(raw_documents)

# Function to generate embeddings using OpenAI
def get_embeddings(text):
     response = openai.embeddings.create(
         model="text-embedding-ada-002",
         input=text
     )
     answer = response.data[0].embedding
     return answer

# Load and process documents
def load_and_process_documents(directory, file_extension):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            with open(os.path.join(directory, filename), 'rb') as file:
                if file_extension == '.json':
                    json_data = json.load(file)
                    content = json_data['content']  # Adjust according to JSON structure
                else:  # PDF processing
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ' '.join([page.extract_text() for page in pdf_reader.pages])
                documents.extend(custom_text_splitter(content, 1000))  # Use the custom text splitter
    return documents
# # Load and process JSON metadata
# json_files = [os.path.join(metadata_directory, f) for f in os.listdir(metadata_directory) if f.endswith('.json')]
# metadata_documents = load_and_process_json(json_files, jq_schema='.chapters[]', text_splitter=text_splitter)

# # Load metadata from the metadata directory
# pdf_metadata = load_metadata(metadata_directory)

# # Load and process PDF data
# # Assuming you have a dictionary `pdf_metadata` where keys are filenames and values are metadata
# pdf_documents = load_and_process_pdf(pdf_directory, pdf_metadata, '.pdf')

# # Format the documents for Chroma
# formatted_metadata_documents = format_for_chroma(metadata_documents)
# formatted_pdf_documents = format_for_chroma(pdf_documents)

# # Combine and create the Chroma database
# db = Chroma.from_documents(formatted_metadata_documents + formatted_pdf_documents, OpenAIEmbeddings(openai_api_key=your_openai_api_key))

# Connect to ChromaDB using Client
chroma_client = chromadb.Client()

# Function to index documents in ChromaDB
def index_documents_in_chroma(documents, client, db_name):
    for doc in documents:
        embedding = get_embeddings(doc)
        client.insert(embedding, doc, db_name=db_name)

# Load and index documents
metadata_documents = load_and_process_documents(metadata_directory, '.json')
pdf_documents = load_and_process_documents(pdf_directory, '.pdf')
index_documents_in_chroma(metadata_documents, chroma_client, db_name='metadata_db')
index_documents_in_chroma(pdf_documents, chroma_client, db_name='pdf_db')

def get_gpt4_chat_response(prompt, context):
    # Function to get a response from GPT-4 using OpenAI API.
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a tax law expert AI to assist the legal profession. You provide the legal profession with the best knowledge and analyses based on the client's statement the legal profession has shared. It doesn't matter if your analysis is incomplete because it is just a reference. The legal profession will properly advise referring to your analysis as a reference. Generate response in the same language as the CLIENT ASKING."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {prompt}"}
        ],
        max_tokens=500
    )    
    answer = response.choices[0].message.content
    return answer

# Streamlit UI
st.title('ChatGPT based on Tax Law')
st.write('Type your question related to the Tax Law and get an answer.')

# Input text box for user to ask questions
user_input = st.text_input('Ask a question:')

# Search and Response Logic
if user_input:
    query_embedding = get_embeddings(user_input)
    context = ''

    # Search in metadata
    metadata_results = chroma_client.search(query_embedding, k=1, db_name='metadata_db')
    if metadata_results:
        context = metadata_results[0]['data']
    else:
        # Search in PDF documents if no results found in metadata
        pdf_results = chroma_client.search(query_embedding, k=1, db_name='pdf_db')
        if pdf_results:
            context = pdf_results[0]['data']

    # Generate GPT-4 chat response
    if context:
        gpt4_response = get_gpt4_chat_response(user_input, context)
        st.write('GPT-4 Response:', gpt4_response)
    else:
        st.write('No relevant information found for your query.')

# # Search and Response Logic
# if user_input:
#     query_embeddings = get_embeddings(user_input)

#     # Search in metadata
#     metadata_results = db.search(query_embeddings, num_results=1, documents=metadata_documents)
#     if metadata_results:
#         # Extracting the relevant metadata content
#         metadata_content = metadata_results[0]['document']['content']
#         # Format and display the metadata information
#         st.write('Relevant Metadata:', metadata_content)
#         # You can also use this content to inform the ChatGPT response

#     # Search in PDF documents
#     pdf_results = db.search(query_embeddings, num_results=1, documents=pdf_documents)
#     if pdf_results:
#         # Extracting the relevant PDF content
#         pdf_content = pdf_results[0]['document']['content']
#         # Process and display the PDF information
#         st.write('Relevant PDF Content:', pdf_content)
#         # Use this content to guide the ChatGPT response

#     # Generate ChatGPT response
#     reply = get_response(user_input)
#     st.write('Response:', reply)
# else:
#     st.write('No relevant documents found.')