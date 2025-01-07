import React, { useState, useEffect, useRef } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatView from './components/ChatView';
import ChatInput from './components/ChatInput';
import ChatTickets from './components/ChatTickets';
import { getListMessages, sendMessage, renameChat, chatInfo } from '@/scripts/chat';



export default function ChatPage({ }) {
    // Chat global information
    const [chatId, setChatId] = useState('');
    const [chatName, setChatName] = useState('Chat Title');
    const [chatNameError, setChatNameError] = useState('');
    // Chat content
    const [listMessages, setListMessages] = useState([]);
    const [listErrors, setListErrors] = useState('');
    const [postMessage, setPostMessage] = useState('');
    const abortControllerRef = useRef(null);
    const [sendError, setSendError] = useState('');
    const [focusOn, setFocusOn] = useState(-1);
    const [isBusy, setBusy] = useState(false);
    const [responseError, setError] = useState(null);


    function modifyChatName(name) {
        setChatNameError("");
        const response = renameChat(chatId, name);
        response.then((response) => {
            if (response.error) {
                setChatNameError(`Failed to rename chat (${response.message})`);
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

    // On postMessage change, send message to chat
    useEffect(() => {
        setSendError("")
        if (postMessage.length > 0) {
            // Send message to chat
            setBusy(true)
            abortControllerRef.current = new AbortController();
            const signal = abortControllerRef.current.signal;
            const response = sendMessage(chatId, postMessage, signal);
            // Handle the stream response
            response.then((response) => {
                const reader = response.body.getReader();
                return new ReadableStream({
                    start(controller) {

                        function push() {
                            return reader.read().then(({ done, value }) => {
                                if (done) {
                                    setBusy(false);
                                    controller.close();
                                    return;
                                }
                                const chunk = new TextDecoder("utf-8").decode(value);
                                controller.enqueue(chunk);
                                return push();
                            });
                        }

                        push();
                    }

                })
            })
                .catch(handleError)
                .then(handleStream)
            setPostMessage('');
        }

    }, [postMessage]);

    function handleStream(stream) {
        const reader = stream.getReader();
        const lm = listMessages;
        let isCancelled = false;
        let accumulatedChunks = '';
        let completedReply = '';
        setListMessages([...lm, { "source": "model", status: 0, "parts": { answer: '', references: [] } }])

        function process({ done, value }) {
            if (isCancelled) return; // Arrêter si annulé
            if (!done) {
                // Extract json
                accumulatedChunks += value
                let jsonMessages;
                let isValidChunk = false;
                if (accumulatedChunks.indexOf('data: ') !== -1) {
                    jsonMessages = accumulatedChunks.split('data: ').filter(Boolean);
                    isValidChunk = true;
                }

                if (isValidChunk) {
                    accumulatedChunks = jsonMessages.pop(); // Keep the incomplete message for the next iteration
                    completedReply = handleChunk(jsonMessages, completedReply);
                    setListMessages([...lm, { "source": "model", status: 0, "parts": completedReply }])
                }
                return reader.read().then(process);
            }
            else {
                const parts = JSON.parse(completedReply);
                setListMessages([...lm, { "source": "model", status: 1, "parts": parts }])
            }
        }

        reader.read().then(process).catch(
            (error) => {
                if (error.name !== 'AbortError') {
                    console.log(error);
                }

            }
        );

        return () => {
            isCancelled = true;
            reader.cancel();
        }
    }

    useEffect(() => {
        console.log(isBusy);
    }, [isBusy]);

    function handleError(error) {
        setBusy(false);
        console.log(error)
    }


    function handleChunk(jsonMessages, completedReply) {
        for (const jsonMsg of jsonMessages) {
            if (jsonMsg.trim() !== '') {
                const msg = JSON.parse(jsonMsg);
                let reply = '';
                // Extract the generated reply from the response
                if (msg.choices[0].finish_reason !== 'stop') {
                    reply = msg.choices[0].delta.content;
                }

                // Handle the generated reply as desired
                if (reply) {
                    completedReply += reply;
                }
            }
        }
        return completedReply;
    }

    function abortResponse() {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
            setBusy(false);
        }
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
                <ChatTickets listMessages={listMessages} focusOn={focusOn} />
                {listErrors && (
                    <p className='text-red-500'>
                        {listErrors}
                    </p>
                )}
                <ChatInput sendInput={send} isBusy={isBusy} abortResponse={abortResponse} />
                {responseError && (
                    <p>
                        {responseError}
                    </p>
                )}
            </div>
        </div>
    )
}