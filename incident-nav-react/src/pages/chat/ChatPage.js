import React, { useState, useEffect, useContext, useRef } from 'react';
import { Link } from 'react-router-dom';
// Components
import ChatHeader from './components/ChatHeader';
import ChatView from './components/ChatView';
import ChatInput from './components/ChatInput';
import ChatTickets from './components/ChatTickets';
import { getListMessages, sendMessage, renameChat, chatInfo } from '@/scripts/chat';
import { AuthContext } from '../../components/auth/AuthContext';


export default function ChatPage({ chatId }) {
    const [loading, setLoading] = useState(true);
    const [loadingError, setLoadingError] = useState(null);
    // Chat global information
    const [chatName, setChatName] = useState('');
    const [chatNameError, setChatNameError] = useState('');
    // Chat content
    const [listMessages, setListMessages] = useState([]);
    const [postMessage, setPostMessage] = useState('');
    const abortControllerRef = useRef(null);
    const [sendError, setSendError] = useState('');
    const [focusOn, setFocusOn] = useState(-1);
    const [isBusy, setBusy] = useState(false);
    const [responseError, setError] = useState(null);

    const { user } = useContext(AuthContext);
    const currentUser = user;
    const industries = [];
    currentUser.industries.forEach(industry => {
        industries.push(industry.name)
    });

    const modifyChatName = (name) => {
        setChatNameError("");
        const response = renameChat(chatId, name);
        response.then((response) => {
            if (response.error) {
                setChatNameError(`Failed to rename chat (${response.message})`);
            }
        })
    }

    // Send message to chat
    const send = (msg) => {
        // Update list message
        setListMessages([...listMessages, { source: 'user', status: 1, parts: { answer: msg, references: [] } }]);
        // Send message
        setPostMessage(msg);
    }

    const handlePostMessageChange = (event) => {
        setSendError("")
        if (postMessage.length > 0) {
            // Send the message
            setBusy(true);
            const previousMessages = listMessages;
            setListMessages([...previousMessages, { source: 'model', status: 0, parts: { answer: "Responding...", references: [] } }]);
            abortControllerRef.current = new AbortController()

            sendMessage(chatId, postMessage, industries, abortControllerRef.current.signal)
                .then(async (response) => {
                    const jsonResponse = await response.json();
                    setListMessages([...previousMessages, jsonResponse?.data]);
                })
                .catch((error) => {
                    if (error.name === 'AbortError') {
                        setListMessages([...previousMessages, { source: 'model', status: -1, parts: { answer: "Request aborted", references: [] } }]);
                    }
                })
                .finally(() => {
                    setBusy(false);
                    setPostMessage('');
                });
        }
    }

    useEffect(() => {
        handlePostMessageChange();
    }, [postMessage]);

    function handleError(error) {
        setBusy(false);
        setError(error);
        console.error(error)
    }

    function abortResponse() {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
            setBusy(false);
        }
    }

    const requestChatInfo = (chatId) => {
        chatInfo(chatId).then((response) => {
            if (response.id === chatId) {
                setChatName(response.name);
            }
        }).catch((error) => {
            setLoadingError(`Failed to load chat (${error})`);
        })  
        
        
    }

    const requestListMessages = async (chatId) => {
        getListMessages(chatId).then((response) => {
            if (response.chat_id === chatId) {
                setListMessages(response.messages);
            }
        }).catch((error) => {
            setLoadingError(`Failed to load chat (${error})`);
        })
    }

    // On page load, get chat ID from URL and update chat
    useEffect(() => {
        setLoading(true);
        setLoadingError(null);
        if (chatId) {
            requestChatInfo(chatId);
            requestListMessages(chatId);
        } else {
            setLoadingError("Chat ID not found");
        }
        setLoading(false);
    }, []);

    return (
        <div className='flex flex-col items-center justify-center w-full h-full'>
            <ChatHeader chatName={chatName} setChatName={modifyChatName} renameError={chatNameError} />
            <div className='container flex flex-col w-full xl:w-[60%] h-[90%] items-center justify-center p-2 gap-2 rounded-3xl bg-black/10' id='chat-container'>

                {loading || loadingError ? (
                    // Loading spinner
                    <div className='flex items-center justify-center w-full h-full'>
                        {loading && (
                            <div className="animate-spin rounded-full h-32 w-32 border-t-1 border-b-2 border-light-accent"></div>
                        )}
                        {loadingError && (
                            <div className="flex flex-col items-center justify-center gap-2">
                                <p className="text-light-alert dark:text-dark-alert">
                                    {loadingError}
                                </p>
                                <Link to="/chat" className="text-accent underline hover:text-accent hover:underline">
                                    Go back
                                </Link>
                            </div>
                        )}
                    </div>
                ) : (
                    // Chat content
                    <>
                        <ChatView listMessages={listMessages} setFocusOn={setFocusOn} />
                        <ChatTickets listMessages={listMessages} focusOn={focusOn} />
                        {responseError && (
                            <p>
                                {responseError}
                            </p>
                        )}
                        <ChatInput sendInput={send} isBusy={isBusy} abortResponse={abortResponse} style={{ enable: !isBusy, error: sendError }} />
                        {sendError && (
                            <p>
                                {sendError}
                            </p>
                        )}
                    </>
                )}


            </div>
        </div>
    )
}