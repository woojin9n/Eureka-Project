__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import openai
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
# Set up PDF files
loader = PyPDFDirectoryLoader("./data/")

# Load the document, split it into chunks
raw_documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)

# embed each chunk and load it into the vector store.
db = Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key='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'))

# Set up OpenAI API Key
openai.api_key = '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'

def get_response(prompt):
    """Function to get a response from GPT-4 using OpenAI API."""
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a tax law expert AI to assist the legal profession. You provide the legal profession with the best knowledge and analyses based on the client's statement the legal profession has shared. It doesn't matter if your analysis is incomplete because it is just a reference. The legal profession will properly advise referring to your analysis as a reference. Generate response in the same language as the CLIENT ASKING."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    
    # Accessing the response data directly, assuming the 'response' object has the necessary method/attribute
    answer = response.get("choices")[0].get("message")["content"].strip()
    return answer

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
