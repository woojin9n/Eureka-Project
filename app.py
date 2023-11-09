import streamlit as st
import openai
import os
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
db = Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")))

# Set up OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
def get_response(prompt):
    """Function to get a response from GPT-4 using OpenAI API."""
    response = openai.Completion.create(
      model="gpt-4",
      prompt=prompt,
      max_tokens=150
    )
    message = response.choices[0].text.strip()
    return message

# Streamlit UI
st.title('ChatGPT based on Chroma Vector Store')
st.write('Type your question related to the documents in Chroma Vector Store and get an answer.')

# Input text box for user to ask questions
user_input = st.text_input('Ask a question:')

if user_input:
    # TODO: You might want to preprocess or append context from your vector store
    # to the user input before passing to the GPT model.
    
    response = get_response(user_input)
    st.write('Response:', response)
