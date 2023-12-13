from flask import Flask, request, jsonify
app = Flask(__name__)

# 일반적인 라우트 방식입니다.
@app.route('/a')
def index():
    return jsonify({"response": "aaa"})
    
if __name__ == '__main__':
    app.run(debug=True)
