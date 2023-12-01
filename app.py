from flask import Flask, render_template, request, jsonify
import os
import openai
# import json
# import PyPDF2
# import chromadb

app = Flask(__name__)

# Set up OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up directories for PDF files and metadata
pdf_directory = "./data/"
metadata_directory = "./metadata/"

# # Custom text splitter function
# def custom_text_splitter(text, chunk_size=1000):
#     return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# # Connect to ChromaDB using Client
# chroma_client = chromadb.Client()

# # Function to index documents in ChromaDB
# def index_documents_in_chroma(documents, client, db_name):
#     for doc in documents:
#         embedding = get_embeddings(doc)
#         client.add(embedding, doc, db_name=db_name)

# # Function to generate embeddings using OpenAI
# def get_embeddings(text):
#     response = openai.embeddings.create(
#         model="text-embedding-ada-002",
#         input=text
#     )
#     answer = response.data[0].embedding
#     return answer

# # Function to get a response from GPT-4 using OpenAI API
# def get_gpt4_chat_response(prompt, context):
#     response = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a tax law expert AI to assist the legal profession. You provide the legal profession with the best knowledge and analyses based on the client's statement the legal profession has shared. It doesn't matter if your analysis is incomplete because it is just a reference. The legal profession will properly advise referring to your analysis as a reference. Generate response in the same language as the CLIENT ASKING."},
#             {"role": "user", "content": f"Context: {context}\nQuestion: {prompt}"}
#         ],
#         max_tokens=500
#     )    
#     answer = response.choices[0].message.content
#     return answer

# Upload a file with an "assistants" purpose
metafile = openai.files.create(
  file=open(os.listdir(path=metadata_directory), "rb"),
  purpose='assistants'
)

datafile = openai.files.create(
  file=open(os.listdir(path=pdf_directory), "rb"),
  purpose='assistants'
)

# Set up Assistant API
assistant = openai.beta.assistants.create(
    name="Tax Law chatbot",
    instructions="The main role of the tax law chatbot is to provide answers and solutions to questions requested by users, utilizing its tax law expertise and, now, the latest information in the OpenAI API documentation. Your job is to provide accurate tax law information in the context of the need, first by finding the appropriate content for the user's question in the JSON file data, and then by finding the appropriate content in the PDF file data related to the JSON file data. If a request is vague or incomplete, ask for more details to ensure an accurate and helpful response. Maintain a friendly and approachable tone while maintaining a professional demeanor. Treat users with respect and courtesy, and provide personalized answers when possible. ",
    tools=[{"type": "retrieval"}],
    model="gpt-4-1106-preview",
    file_ids=[metafile.id, datafile.id]
)

thread = openai.beta.threads.create()

# # Load and process documents
# def load_and_process_documents(directory, file_extension):
#     documents = []
#     for filename in os.listdir(directory):
#         if filename.endswith(file_extension):
#             with open(os.path.join(directory, filename), 'rb') as file:
#                 if file_extension == '.json':
#                     json_data = json.load(file)
#                     content = json_data['chapters']  # Adjust according to JSON structure
#                 else:  # PDF processing
#                     pdf_reader = PyPDF2.PdfReader(file)
#                     content = ' '.join([page.extract_text() for page in pdf_reader.pages])
#                 documents.extend(custom_text_splitter(content, 1000))  # Use the custom text splitter
#     return documents

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_input = data.get('query')

    message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input
    )

    run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions=message
    )
    
    run = openai.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
    )

    messages = openai.beta.threads.messages.list(
    thread_id=thread.id
    )
    
    return jsonify({"response": messages})

    # query_embedding = get_embeddings(user_input)
    # context = ''

    # # Search in metadata
    # metadata_results = chroma_client.search(query_embedding, k=1, db_name='metadata_db')
    # if metadata_results:
    #     context = metadata_results[0]['data']
    # else:
    #     # Search in PDF documents if no results found in metadata
    #     pdf_results = chroma_client.search(query_embedding, k=1, db_name='pdf_db')
    #     if pdf_results:
    #         context = pdf_results[0]['data']

    # # Generate GPT-4 chat response
    # if context:
    #     gpt4_response = get_gpt4_chat_response(user_input, context)
    #     return jsonify({"response": gpt4_response})
    # else:
    #     return jsonify({"response": "No relevant information found for your query."})

if __name__ == '__main__':
    app.run(debug=True)
