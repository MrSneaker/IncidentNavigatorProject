async function newChat() {
    const reponse = await fetch('/chat/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ name: 'New Chat' })
    })

    // Check if the response is an error (not 2xx)
    if (reponse.status >= 300) {
        return { error: reponse.status, message:  reponse.message? reponse.message : reponse.statusText }
    }

    try {
        // Parse the response
        const data = await reponse.json()
        return data

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
        return { error: response.status, message:  response.message? response.message : response.statusText }
    }

    // Parse the response
    try {
        const data = await response.json()
        return data
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function listChats() {
    const reponse = await fetch('/chat/list', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    
    // Check if the response is an error (not 2xx)
    if (reponse.status >= 300) {
        return { error: reponse.status, message:  reponse.message? reponse.message : reponse.statusText }
    }

    // Parse the response
    try {
        const data = await reponse.json()
        return data
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function getListMessages(chat_id) {
    const reponse = await fetch(`/chat/msgs?chat_id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
    })
    if (reponse.status >= 300) {
        return { error: reponse.status, message:  reponse.message? reponse.message : reponse.statusText }
    }
    const response_json = await reponse.json()
    const data = response_json?.data
    return data
}

async function sendMessage(chat_id, message, abortSignal) {
    const reponse = await fetch(`/chat/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        signal: abortSignal,
        body: JSON.stringify({  : chat_id, parts: message })
    })
    return reponse
}

async function renameChat(chat_id, name) {
    const reponse = await fetch(`/chat/rename`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ id: chat_id, name: name })
    })
    if (reponse.status >= 300) {
        return { error: reponse.status, message:  reponse.message ? reponse.message : reponse.statusText }
    }
    try {
        const data = await reponse.json()
        return data
    } catch (error) {
        return { error: -1, message: 'Invalid response' }
    }
}

async function chatInfo(chat_id) {
    const reponse = await fetch(`/chat/info?id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    const response_json = await reponse.json()
    const data = response_json?.data
    return data
}

export { newChat, delChat, listChats, getListMessages, sendMessage, renameChat, chatInfo }