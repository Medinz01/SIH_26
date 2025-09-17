const searchBox = document.getElementById('search-box');
const resultsList = document.getElementById('results-list');
const fhirOutput = document.getElementById('fhir-output');
const saveButton = document.getElementById('save-button');

let currentFhirCondition = null;
const MOCK_ABHA_TOKEN = "abhatoken_for_sih_demo_25026"; // The secret key

const searchTerms = async (event) => {
    // ... (this function remains the same as before)
    const query = event.target.value;
    if (query.length < 2) {
        resultsList.innerHTML = '';
        return;
    }
    try {
        const response = await fetch(`/search?term=${query}`);
        const results = await response.json();
        resultsList.innerHTML = '';
        results.forEach(term => {
            const li = document.createElement('li');
            li.textContent = `${term.term} (${term.code})`;
            li.dataset.id = term.id;
            li.onclick = selectTerm;
            resultsList.appendChild(li);
        });
    } catch (error) {
        console.error('Search failed:', error);
        resultsList.innerHTML = '<li>Error loading results.</li>';
    }
};

const selectTerm = async (event) => {
    // ... (this function is slightly modified to store the resource)
    const termId = event.target.dataset.id;
    resultsList.innerHTML = '';
    searchBox.value = event.target.textContent;
    fhirOutput.textContent = 'Loading...';
    saveButton.style.display = 'none';

    try {
        const response = await fetch(`/fhir/condition/${termId}`);
        currentFhirCondition = await response.json(); // Store the FHIR resource
        fhirOutput.textContent = JSON.stringify(currentFhirCondition, null, 2);
        saveButton.style.display = 'block'; // Show the save button
    } catch (error) {
        console.error('FHIR generation failed:', error);
        fhirOutput.textContent = 'Error generating FHIR resource.';
    }
};

// --- NEW FUNCTION ---
const saveToEMR = async () => {
    if (!currentFhirCondition) return;

    alert('Submitting to secure endpoint...');

    // Create a FHIR Transaction Bundle
    const bundle = {
        resourceType: "Bundle",
        type: "transaction",
        entry: [{
            resource: currentFhirCondition,
            request: {
                method: "POST",
                url: "Condition"
            }
        }]
    };

    try {
        const response = await fetch('/bundle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': MOCK_ABHA_TOKEN // This is our secure token!
            },
            body: JSON.stringify(bundle)
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Success: ${result.message}`);
        } else {
            throw new Error(result.detail || 'Save failed');
        }

    } catch (error) {
        console.error('Save to EMR failed:', error);
        alert(`Error: ${error.message}`);
    }
};

searchBox.addEventListener('keyup', searchTerms);
saveButton.addEventListener('click', saveToEMR);