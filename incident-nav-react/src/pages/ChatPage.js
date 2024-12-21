import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { IoMdArrowBack } from "react-icons/io";
import { FiEdit } from "react-icons/fi";
import { IoSend as SendIcon } from "react-icons/io5";
import { FaStop as StopIcon } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

import { listMessages, sendMessage, renameChat, chatInfo } from '../scripts/chat';

export default function ChatPage() {
    const [currentChatName, setCurrentChatName] = useState('Chat Title');
    const [chatName, setChatName] = useState('Chat Title');
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [chatId, setChatId] = useState('');
    const [postValue, setPostValue] = useState('');

    function onChatNameChange(id, name) {
        // Update the chat name
        setCurrentChatName(name);

        // Send the new chat name to the server
        const response = renameChat(id, name);
        response.then((response) => {
            if (response.status === 200) {
                console.log('Chat name updated successfully');
            }
        }).catch((error) => {
            setError(error);
        });
    }



    function updateListMessages(id) {
        listMessages(id).then((response) => {
            if (response.chat_id === id) {
                setMessages(response.messages);
            }
        });
    }

    function scrollToBottom() {
        const scrollarea = document.getElementById("chat-container")
        if (scrollarea) {
            scrollarea.scrollTop = scrollarea.scrollHeight
        }
    }

    function send() {
        if (message.length === 0) return;
        setMessages([...messages, { source: 'user', parts: message }]);
        setPostValue(message);
        setMessage('');
    }


    useEffect(() => {
        if (postValue.length > 0) {
            // Send the message to the server
            const response = sendMessage(chatId, postValue);

            // Handle the response
            response.then((response) => {
                const reader = response.body.getReader();
                return new ReadableStream({
                    start(controller) {

                        function push() {
                            return reader.read().then(({ done, value }) => {
                                if (done) {
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
                });
            }).then((stream) => {
                handleStream(stream);
            }).catch((error) => {
                setError(error)
            });

            // Clear the post value
            setPostValue('');
        }
    }, [postValue]);


    useEffect(() => {
        scrollToBottom();
    }, [messages])

    function handleStream(stream) {
        const reader = stream.getReader();
        const lm = messages;
        let accumulatedChunks = '';
        let completedReply = '';

        reader.read().then(value => {
            function process({ done, value }) {
                try {
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
                            setMessages([...lm, { "source": "model", "parts": completedReply }])
                        }
                        return reader.read().then(value => { process(value) })
                    }

                } catch (error) {
                    setBusy(false);
                    setError(error);
                }

            }
            process(value);
        });
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

    useEffect(() => {
        if (error.length > 0) {
            console.error(error);
        }
    }, [error]);

    // get the chat id from the url
    useEffect(() => {
        const url = window.location.href;
        const id = url.split('/').pop();

        setChatId(id);
        const chat = chatInfo(id);
        chat.then((response) => {
            setCurrentChatName(response.name);
            setChatName(response.name);
        });
        updateListMessages(id);
    }, []);


    return (
        <div className="flex flex-col items-start justify-start h-full w-full gap-2 overflow-hidden">

            <div className="flex items-center justify-between w-full p-2 gap-4">
                <Link to="/chat" className="text-2xl font-bold"> <IoMdArrowBack /> </Link>
                <div className="relative text-2xl font-bold w-full flex items-center justify-center">
                    <div className='w-full h-full flex items-center justify-center max-w-[400px]'>
                        <input
                            type="text"
                            className="bg-transparent p-2 m-0 text-2xl font-bold rounded-lg text-center border border-transparent hover:border-light-background hover:dark:border-dark-background focus:border-light-accent focus:dark:border-light-accent outline-none hover:bg-black/2"
                            value={chatName}
                            placeholder="Untitled Chat"
                            onFocus={(e) => e.target.nextSibling.style.display = 'none'}
                            onBlur={(e) => {
                                e.target.nextSibling.style.display = 'block'
                                if (chatName !== currentChatName) {
                                    onChatNameChange(chatId, chatName);
                                }
                            }}
                            onChange={(e) => setChatName(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    e.target.blur();
                                }
                            }}
                        />
                        <FiEdit
                            className="relative top-0 right-0 text-2xl font-bold text-white transform -translate-x-[40px] hover:cursor-pointer"
                        />
                    </div>
                </div>
            </div>

            <div className="w-full h-[1px] bg-black/20"></div>

            <div className="flex flex-row h-[92%] w-full items-center justify-center p-5">
                <div className="w-full xl:w-[60%] h-full flex flex-col items-center justify-center p-2 gap-2 rounded-3xl bg-light-surface dark:bg-dark-surface shadow-lg">
                    <div className="w-full h-full p-2 gap-2 overflow-y-auto" id="chat-container">
                        {messages.map((message, index) => (
                            <div key={index} className="flex flex-row items-center justify-start gap-2">
                                {message.source === 'user' ? (
                                    <div className="flex flex-row w-full items-end justify-end gap-2">
                                        <div className="p-2 px-[15px] m-1 min-w-[40px] max-w-[65%] rounded-lg rounded-br-none bg-dark-accent text-light-surface break-words">
                                            <ReactMarkdown>{message.parts}</ReactMarkdown>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex flex-row w-full items-start justify-start gap-2">

                                        <div className="p-2 min-w-[40px] max-w-[65%] px-[15px] m-1 rounded-lg rounded-bl-none bg-black/20 break-words">
                                            <ReactMarkdown className="text-left">
                                                {message.parts}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    <form className="p-[5px] gap-2 search-section flex flex-row w-full h-[50px] shadow-md rounded-full bg-black/10" onSubmit={(e) => { e.preventDefault(); send(); }}>
                        <input
                            type="text"
                            className="pl-[25px] w-full rounded-full bg-transparent border-gray-300 focus:border-dark-accent focus:outline-none "
                            placeholder="Type a message..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                        />
                        <button
                            type="submit"
                            className="rounded-full flex items-center justify-center bg-light-accent dark:bg-dark-accent disabled:opacity-30"
                            disabled={message.length === 0 || busy}>
                            {busy ? (
                                <StopIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                            ) : (
                                <SendIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                            )}
                        </button>
                    </form>

                </div>


            </div>
        </div>
    )

}