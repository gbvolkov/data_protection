function toggleResponses() {
    const llmDiv = document.getElementById('llm_response');
    const deanDiv = document.getElementById('dean_response');
    const view = document.querySelector('input[name="view"]:checked').value;
    llmDiv.hidden = (view !== 'llm');
    deanDiv.hidden = (view !== 'dean');
}