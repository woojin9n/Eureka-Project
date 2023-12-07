function processUserInput(data) {
    fetch("/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        displayResponse(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displayResponse(data) {
    const responseContainer = document.getElementById('response-container');
    const gpt4Response = data.response;
    responseContainer.innerHTML = `<p><strong>GPT-4 Response:</strong> ${gpt4Response}</p>`;
    responseContainer.style.display = 'block';
}

