document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    submitButton.addEventListener("click", () => {
        const userQuery = userInput.value;

        // You can make a POST request to your Python backend to handle the user query and retrieve a response.
        // Here's a simplified example using Fetch API:
        fetch("/api/get_response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: userQuery }),
        })
        .then((response) => response.json())
        .then((data) => {
            const gpt4Response = data.response;
            responseContainer.innerHTML = `<p><strong>GPT-4 Response:</strong> ${gpt4Response}</p>`;
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    });
});
