import time
from flask import Flask, render_template, request, jsonify, current_app
import os
import openai

app = Flask(__name__)

# Set up OpenAI API Key
openai.api_key = "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"

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

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

# js에서 get_response로 json객체 호출
@app.route('/get_response/', methods=['GET','POST']) 
def get_response():
    #  current_app.logger.info("INFO 레벨로 출력")
    data = request.get_json(silent=True)
    user_input = data.get('question')
    current_app.logger.info("user_input="+user_input)

    # message 객체 생성
    message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input
    )

    # run 객체 생성
    current_app.logger.info("message=[]")
    run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="2-3team creative reserved!!!"
    )

    """
    current_app.logger.info("222")
    run = openai.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
    )
    """

    # 응답이 올 때 까지 대기    
    while True:
        if run.status == "completed":
            break
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id, 
            run_id=run.id
        )
        # print(run)
        time.sleep(1)

    # 응답이 완료되면 messages를 받아온다
    messages = openai.beta.threads.messages.list(
    thread_id=thread.id
    )


    print(messages)
    #print(messages.data[0].content[0].text.value)

    """
    # 각 메시지에서 'value' 추출 및 출력
    for msg in messages.data:
        for content in msg.content:
            if content.type == 'text':
                print(content.text.value)
    """
    # list객체라 0번째 것만 받아옴
    return jsonify({"response": messages.data[0].content[0].text.value})

if __name__ == '__main__':
    app.run(debug=True)
