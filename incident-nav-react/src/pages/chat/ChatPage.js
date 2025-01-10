import React, { useState, useEffect, useContext } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatView from './components/ChatView';
import ChatInput from './components/ChatInput';
import ChatTickets from './components/ChatTickets';
import { getListMessages, sendMessage, renameChat, chatInfo } from '@/scripts/chat';
import { AuthContext } from '../../components/auth/AuthContext';



export default function ChatPage({ }) {
    // Chat global information
    const [chatId, setChatId] = useState('');
    const [chatName, setChatName] = useState('Chat Title');
    const [chatNameError, setChatNameError] = useState('');
    // Chat content
    const [listMessages, setListMessages] = useState([]);
    const [postMessage, setPostMessage] = useState('');
    const [focusOn, setFocusOn] = useState(-1);
    const [isBusy, setBusy] = useState(false);
    const [responseError, setError] = useState(null);
    let abortController = new AbortController();

    const { user } = useContext(AuthContext);
    const currentUser = user;
    const industries = [];
    currentUser.industries.forEach(industry => {
        industries.push(industry.name)
    });

    function modifyChatName(name) {
        const response = renameChat(chatId, name);
        response.then((response) => {
            if (response.error) {
                setChatNameError(`Error ${response.error}: ${response.message}`);
            }
        })
    }

    // Send message to chat
    function send(msg) {
        // Update list message
        setListMessages([...listMessages, { source: 'user', status: 1, parts: { answer: msg, references: [] } }]);
        // Send message
        setPostMessage(msg);
    }

    useEffect(() => {
        if (postMessage.length > 0) {
            // Send the message
            setBusy(true);
            abortController = new AbortController()
            sendMessage(chatId, postMessage, industries, abortController.signal)
                .then(async (response) => {
                    const jsonResponse = await response.json();
                    setListMessages((prevMessages) => [
                        ...prevMessages,
                        { source: 'model', status: 1, parts: jsonResponse },
                    ]);
                })
                .catch((error) => {
                    setError(error);
                    console.error('Error while managing answer', error);
                })
                .finally(() => {
                    setBusy(false);
                    setPostMessage('');
                });
        }
    }, [postMessage]);

    function handleError(error) {
        setBusy(false);
        setError(error);
        console.error(error)
    }

    function abortResponse() {
        // TODO
    }

    // On page load, get chat ID from URL and update chat
    useEffect(() => {
        // Get chat ID from URL
        const url = window.location.href;
        const id = url.split('/').pop();
        setChatId(id);

        const chat = chatInfo(id);
        chat.then((response) => {
            setChatName(response.name);
        });

        // Update the list of message
        getListMessages(id).then((response) => {
            if (response.chat_id === id) {
                setListMessages(response.messages)
            }
        }).catch(handleError);

    }, []);

    return (
        <div className='flex flex-col items-center justify-center w-full h-full'>
            <ChatHeader chatName={chatName} setChatName={modifyChatName} renameError={chatNameError} />
            <div className='container flex flex-col w-full xl:w-[60%] h-[90%] items-center justify-center p-2 gap-2 rounded-3xl bg-black/10' id='chat-container'>
                <ChatView listMessages={listMessages} setFocusOn={setFocusOn} />
                <ChatTickets listMessages={listMessages} focusOn={focusOn}/>
                <ChatInput sendInput={send} isBusy={isBusy} abortResponse={abortResponse} />
                {/* <p>
                    {responseError ? `${responseError.message || responseError.toString()}${responseError.stack ? `\n${responseError.stack.split('\n')[1]}` : ''}` : ''}
                </p> */}
            </div>
        </div>
    )
}