async function getAllLLMs() {
    try {
        const response = await fetch('/llm/llms', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            return { error: false, data: data };
        } else {
            return { error: true, message: 'Failed to fetch LLMs' };
        }
    } catch (error) {
        console.error('Error fetching LLMs:', error);
        return { error: true, message: error.message };
    }
}

async function addLLM(uri, api_key, model) {
    const response = await fetch('/llm/llm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ uri, api_key, model }),
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error adding LLM:', data.message);
    }

    return data;
}

async function deleteLLM(llmId) {
    const response = await fetch(`/llm/llm/${llmId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error deleting LLM:', data.message);
    }

    return data;
}

async function updateLLM(llmId, uri, api_key, model) {
    const response = await fetch(`/llm/llm/${llmId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ uri, api_key, model }),
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error updating LLM:', data.message);
    }

    return data;
}

async function getLLM(llmId) {
    const response = await fetch(`/llm/llm/${llmId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    });

    const data = await response.json();

    if (data.error !== 0) {
        console.error('Error fetching LLM:', data.message);
    }

    return data;
}

export { getAllLLMs, addLLM, deleteLLM, updateLLM, getLLM };
