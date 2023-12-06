document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    submitButton.addEventListener("click", () => {
        const userQuery = userInput.value;
    })
        // Making an AJAX call to the app.py route with the user input
        fetch("/api/get_response", {
            question : userQuery
})
.then((response) => response.json())
.then((data) => {
    const gpt4Response = data.response;
    responseContainer.innerHTML = `<p><strong>GPT-4 Response:</strong> ${gpt4Response}</p>`;
})
.catch((error) => {
    console.error("Error:", error);
});

    // Event listener for the enter key in the input field
    document.getElementById('user-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            submitButton.click();
        }
    });
});
