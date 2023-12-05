document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    submitButton.addEventListener("click", () => {
        const userQuery = userInput.value;

        // Making an AJAX call to the app.py route with the user input
        fetch('/api/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: userQuery })
        })
        .then(response => response.json())
        .then(data => {
            // Displaying the response in the response-container
            responseContainer.innerHTML = `<p>Here is the answer: ${data.response}</p>`;
            responseContainer.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            responseContainer.innerHTML = `<p>Error in fetching response</p>`;
        });
    });

    // Event listener for the enter key in the input field
    document.getElementById('user-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            submitButton.click();
        }
    });
});

