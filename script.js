document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");
    const responseContainer = document.getElementById("response-container");

    submitButton.addEventListener("click", () => {
        
        const userQuery = userInput.value;
        alert("userQuery=" + userQuery);
        
        fetch("/", {
            method: "POST",
            headers: {
                'Accept': "application/json",
                'Content-Type': 'application/json'
              },
            question : userQuery
        }).then(function(res){
                  alert(res);
                  alert(res.json());
                  alert(json.stringfy(res.json()));
               })
        /*
        .then((response) => response.json())
        .then((data) => {
            addHTML(data);
            console.log("data", data);
        })
        */
        .catch((error) => {
            alert(2);
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
