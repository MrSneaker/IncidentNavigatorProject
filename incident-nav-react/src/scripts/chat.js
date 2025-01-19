import { refreshToken } from "./auth";

async function fetchWithToken(url, options, attempt = 0) {
    const response = await fetch(url, options);

    // If Unauthorized (401), try refreshing the token
    if (response.status === 401 && attempt < 3) {
        console.error(`Failed to fetch ${url} with token, refreshing token (attempt ${attempt + 1})`); 
        const refreshResponse = await refreshToken();
        if (refreshResponse.error === 0) {
            // Retry the request with the new token
            options.headers['Authorization'] = `Bearer ${sessionStorage.getItem('token')}`;
            return fetchWithToken(url, options, attempt + 1);
        }
    }

    return response;
}

async function newChat() {
    const response = await fetchWithToken('/chat/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ name: 'New Chat' })
    })

    // Check if the response is an error (not 2xx)
    if (response.status >= 300) {
        return { error: response.status, message:  response.message || response.statusText }
    }

    try {
        return await response.json();   
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }

}

async function delChat(id) {
    const response = await fetchWithToken(`/chat/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ id: id })
    })
    
    // Check if the response is an error (not 2xx)
    if (response.status >= 300) {
        return { error: response.status, message:  response.message || response.statusText }
    }

    // Parse the response
    try {
        return await response.json();
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function listChats() {
    const response = await fetchWithToken('/chat/list', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    
    // Check if the response is an error (not 2xx)
    if (response.status >= 300) {
        return { error: response.status, message:  response.message || response.statusText }
    }

    // Parse the response
    try {
        return await response.json();
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function getListMessages(chat_id) {
    const response = await fetchWithToken(`/chat/msgs?chat_id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
    })
    if (response.status >= 300) {
        return { error: response.status, message:  response.message || response.statusText }
    }
    const response_json = await response.json()
    return response_json?.data;
}

async function sendMessage(chat_id, message, industries, abortSignal) {
    return await fetchWithToken(`/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            },
            signal: abortSignal,
            body: JSON.stringify({ chat_id : chat_id, message: message, industries: industries })
        });
}

async function renameChat(chat_id, name) {
    const response = await fetchWithToken(`/chat/rename`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ id: chat_id, name: name })
    })
    if (response.status >= 300) {
        return { error: response.status, message:  response.message || response.statusText }
    }
    try {
        return await response.json();
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function chatInfo(chat_id) {
    const response = await fetchWithToken(`/chat/info?id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    if (response.status >= 300) {
        throw new Error(response.statusText)
    }
    return await response.json();
}

export { newChat, delChat, listChats, getListMessages, sendMessage, renameChat, chatInfo }