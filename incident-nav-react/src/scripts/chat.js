async function newChat() {
    const response = await fetch('/chat/new', {
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
        // Parse the response
        return await response.json();

    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }

}

async function delChat(id) {
    const response = await fetch(`/chat/delete`, {
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
    const response = await fetch('/chat/list', {
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
    const response = await fetch(`/chat/msgs?chat_id=${chat_id}`, {
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

async function sendMessage(chat_id, message, abortSignal) {
    return await fetch(`/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            },
            signal: abortSignal,
            body: JSON.stringify({ chat_id : chat_id, message: message })
        });
}

async function renameChat(chat_id, name) {
    const response = await fetch(`/chat/rename`, {
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
    const response = await fetch(`/chat/info?id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    const response_json = await response.json()
    return response_json?.data;
}

export { newChat, delChat, listChats, getListMessages, sendMessage, renameChat, chatInfo }