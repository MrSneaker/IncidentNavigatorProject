import React, { useState } from 'react';
import { IoSend as SendIcon } from 'react-icons/io5';
import { FaStop as StopIcon } from 'react-icons/fa';


export default function ChatInput({ isBusy, sendInput, abortResponse, ...props }) {
    const [inputMessage, setInputMessage] = useState('');

    function sendInputMessage(msg) {
        sendInput(msg);
        setInputMessage('');
    }
    
    return (
        <form className="p-[5px] gap-2 search-section flex flex-row w-full h-[50px] shadow-md rounded-full bg-black/10 dark:bg-white/10 " onSubmit={(e) => { e.preventDefault(); }}>
            <input
                type="text"
                className="pl-[25px] w-full rounded-full bg-transparent border-gray-300 focus:border-dark-accent focus:outline-none"
                placeholder="Type a message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
            />
            <button
                type="submit"
                className="rounded-full flex items-center justify-center bg-light-accent dark:bg-dark-accent disabled:opacity-30"
                disabled={inputMessage.length === 0 && !isBusy}
                onClick={
                    () => {
                        if (isBusy) {
                            abortResponse();
                        } else {
                            if (inputMessage.length > 0) {
                                sendInputMessage(inputMessage);
                            }
                        }
                    }
                }
            >
                {isBusy ? (
                    <StopIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                ) : (
                    <SendIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                )}
            </button>
        </form>
    )
}



