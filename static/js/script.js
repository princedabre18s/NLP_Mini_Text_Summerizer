document.getElementById('summaryForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const textArea = document.getElementById('text');
    const fileInput = document.getElementById('fileUpload');
    const length = document.getElementById('length').value;
    const style = document.getElementById('style').value;

    formData.append('length', length);
    formData.append('style', style);

    if (fileInput.files.length > 0) {
        formData.append('fileUpload', fileInput.files[0]);
    } else {
        formData.append('text', textArea.value);
    }

    const resultDiv = document.getElementById('result');
    resultDiv.innerText = "Loading..."; 
    resultDiv.style.display = 'block'; // Make sure the result div is visible
    resultDiv.style.opacity = '0'; // Initial state, invisible

    try {
        // Send the POST request to the Flask server
        const response = await fetch('/summarize', {
            method: 'POST',
            body: formData
        });

        // If the response is not OK, display the error
        if (!response.ok) {
            const errorText = await response.text(); // Get error text
            resultDiv.innerText = `Error: ${errorText}`;
        } else {
            const data = await response.json(); // Parse the JSON response
            if (data.error) {
                resultDiv.innerText = `Error: ${data.error}`;
            } else {
                const summary = data.summary;
                resultDiv.innerText = `Summary:\n${summary}`;
            }
        }

    } catch (error) {
        resultDiv.innerText = `Error: ${error.message}`;
    }

    // Fade-in effect for result
    setTimeout(() => {
        resultDiv.style.opacity = '1'; // Fade in the result div
    }, 100); // Small timeout to allow for the display change
});
