document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    submitButton.addEventListener("click", () => {
        const userQuery = userInput.value;
        fetch("/", {
            headers: {
                Accept: "text/html",
                'Content-Type': 'text/html',
              },
            question : userQuery
        })
        .then((response) => response.json())
        .then((data) => {
            addHTML(data);
        })
        .catch((error) => {console.error("response:", response); 
                           console.error("data:", data);
            console.error("Error:", error);
        });

    })
        // Making an AJAX call to the app.py route with the user input
    function addHTML(data){
        const gpt4Response = data.response;
        responseContainer.innerHTML = `<p><strong>GPT-4 Response:</strong> ${gpt4Response}</p>`;
    }
    // Event listener for the enter key in the input field
    document.getElementById('user-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            submitButton.click();
        }
    });
});
