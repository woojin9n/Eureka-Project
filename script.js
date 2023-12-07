document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    // sendToServer 함수 정의
    function sendToServer(data, callback) {
        fetch("/", {
            method: 'POST',  // POST 요청으로 변경
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)  // 사용자 입력을 JSON으로 변환하여 전송
        })
        .then(response => response.json())
        .then(callback)
        .catch(error => {
            console.error("Error:", error);
        });
    }

    submitButton.addEventListener("click", () => {
        const userQuery = userInput.value;
        sendToServer({ question: userQuery }, addHTML); // sendToServer 함수 호출
    });

    // 서버 응답을 화면에 추가하는 함수
    function addHTML(data) {
        const gpt4Response = data.response;
        responseContainer.innerHTML = `<p><strong>GPT-4 Response:</strong> ${gpt4Response}</p>`;
    }

    // 입력란에서 엔터키 이벤트 리스너
    document.getElementById('user-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            submitButton.click();
        }
    });
});
