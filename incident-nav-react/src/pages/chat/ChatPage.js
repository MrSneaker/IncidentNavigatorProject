import React, { useState, useEffect } from 'react';
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
    const [postMessage, setPostMessage] = useState('');
    const [focusOn, setFocusOn] = useState(-1);
    const [isBusy, setBusy] = useState(false);
    const [responseError, setError] = useState(null);
    let abortController = new AbortController();

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

    // On postMessage change, send message to chat
    useEffect(() => {
        if (postMessage.length > 0) {
            // Send message to chat
            abortController = new AbortController()
            const response = sendMessage(chatId, postMessage, abortController.signal);
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
                                setBusy(true);
                                const chunk = new TextDecoder("utf-8").decode(value);
                                controller.enqueue(chunk);
                                return push();
                            });
                        }

                        push();
                    }

                })
            })
                .then(handleStream)
                .catch(handleError);

            setPostMessage('');
        }

    }, [postMessage]);

    function handleStream(stream) {
        const reader = stream.getReader();
        const lm = listMessages;
        let accumulatedChunks = '';
        let completedReply = '';

        reader.read().then(value => {
            function process({ done, value }) {
                try {
                    if (!done) {
                        setBusy(true);
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
                        return reader.read().then(value => { process(value) })
                    }
                    else {
                        const parts = JSON.parse(completedReply);
                        setListMessages([...lm, { "source": "model", status: 1, "parts": parts }])
                    }
                    setBusy(false);

                } catch (error) {
                    setBusy(false);
                    setError(error);
                }
            }
            process(value);
        });
    }

    function handleError(error) {
        setBusy(false);
        setError(error);
        console.error(error)
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
                <p>
                    {responseError}
                </p>
            </div>
        </div>
    )
}