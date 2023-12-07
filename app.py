from flask import Flask, render_template, request, jsonify
import os
import openai

app = Flask(__name__)

# Set up OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up directories for PDF files and metadata
pdf_directory = "./data/"
metadata_directory = "./metadata/"

# Upload a file with an "assistants" purpose
for filename in os.listdir(metadata_directory):
    if filename.endswith(".json"): 
        file_path = os.path.join(metadata_directory, filename)
        with open(file_path, "rb") as file:
            metafile = openai.files.create(
                file=file,
                purpose='assistants'
            )

for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"): 
        file_path = os.path.join(pdf_directory, filename)
        with open(file_path, "rb") as file:
            datafile = openai.files.create(
                file=file,
                purpose='assistants'
            )

# Set up Assistant API
assistant = openai.beta.assistants.create(
    name="Tax Law chatbot",
    instructions="The main role of the tax law chatbot is to provide answers and solutions to questions requested by users, utilizing its tax law expertise and, now, the latest information in the OpenAI API documentation. Your job is to provide accurate tax law information in the context of the need, first by finding the appropriate content for the user's question in the JSON file data, and then by finding the appropriate content in the PDF file data related to the JSON file data. If a request is vague or incomplete, ask for more details to ensure an accurate and helpful response. Maintain a friendly and approachable tone while maintaining a professional demeanor. Treat users with respect and courtesy, and provide personalized answers when possible. ",
    tools=[{"type": "retrieval"}],
    model="gpt-4-1106-preview",
    file_ids=[metafile.id,datafile.id]
)

thread = openai.beta.threads.create()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assistant', methods=['POST'])
def get_response():
    data = request.json
    user_input = data.get('question')

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

if __name__ == '__main__':
    app.run(debug=True)
