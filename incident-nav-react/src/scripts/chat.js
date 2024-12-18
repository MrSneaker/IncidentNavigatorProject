async function newChat() {
    const chat = await fetch('/api/chat/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    return chat
}

async function delChat(id) {
    const chat = await fetch(`/api/chat/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: id })
    })
    return chat
}


async function listChats() {
    const reponse = await fetch('/api/chat/list', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const chats = await reponse.json()
    return chats.data
}


export { newChat, delChat, listChats };