async function newChat() {
    try {
        const chat = await fetch('/chat/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            },
            body: JSON.stringify({ name: 'New Chat' })
        })
        return chat
    } catch (error) {
        console.error(error)
        return null
    }

}

async function delChat(id) {
    const chat = await fetch(`/chat/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ id: id })
    })
    return chat
}

async function listChats() {
    try{
        const reponse = await fetch('/chat/list', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionStorage.getItem('token')}`
            }
        })
        const chats = await reponse.json()
        return chats.data
    } catch (error) {
        console.error(error)
        return []
    }
}

async function listMessages(chat_id) {
    const reponse = await fetch(`/chat/msgs?chat_id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
    })
    const response_json = await reponse.json()
    const data = response_json?.data
    return data
}

async function sendMessage(chat_id, message, abortSignal){
    const reponse = await fetch(`/chat/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        signal: abortSignal,
        body: JSON.stringify({ chat_id: chat_id, parts: message })
    })
    return reponse
}

async function renameChat(chat_id, name){
    const reponse = await fetch(`/chat/rename`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        },
        body: JSON.stringify({ id: chat_id, name: name })
    })

    return reponse
}

async function chatInfo(chat_id){
    const reponse = await fetch(`/chat/info?id=${chat_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionStorage.getItem('token')}`
        }
    })
    const response_json = await reponse.json()
    console.log(response_json)
    const data = response_json?.data
    return data
}

export { newChat, delChat, listChats, listMessages, sendMessage, renameChat, chatInfo }