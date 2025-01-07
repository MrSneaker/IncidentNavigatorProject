import React, { useEffect, useState } from 'react';
import { IoSend as SendIcon } from 'react-icons/io5';
import { FaStop as StopIcon } from 'react-icons/fa';

export default function ChatInput({ isBusy, sendInput, abortResponse, ...props }) {
    const [inputMessage, setInputMessage] = useState('');
    const [nRow, setNRow] = useState(1);

    function sendInputMessage(msg) {
        sendInput(msg);
        setInputMessage('');
    }

    function onInputChange(e) {
        setInputMessage(e.target.value);
    }

    useEffect(() => {
        const n = inputMessage.split('\n').length
        setNRow(Math.min(Math.max(n, 1), 3))
    }, [inputMessage])

    return (
        <form
            className="search-section bg-black/10 dark:bg-white/10 flex flex-row items-end w-full shadow-md rounded-3xl p-[5px] gap-2 "
            onSubmit={(e) => {
                e.preventDefault();
            }}
            onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (isBusy) {
                        abortResponse();
                    } else {
                        if (inputMessage.length > 0) {
                            sendInputMessage(inputMessage);
                        }
                    }
                }
            }}
        >
            <textarea
                className="pl-[25px] min-h-[40px] pt-2 w-full rounded-full bg-transparent border-gray-300 focus:border-dark-accent focus:outline-none resize-none"
                placeholder="Type a message..."
                value={inputMessage}
                onChange={onInputChange}
                rows={nRow}
                disabled={isBusy}
            />
            <button
                type="submit"
                className="rounded-full flex items-center justify-center bg-light-accent dark:bg-dark-accent disabled:opacity-30"
                disabled={inputMessage.length === 0 && !isBusy}
                onClick={() => {
                    if (isBusy) {
                        abortResponse();
                    } else {
                        if (inputMessage.length > 0) {
                            sendInputMessage(inputMessage);
                        }
                    }
                }}
            >
                {isBusy ? (
                    <StopIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                ) : (
                    <SendIcon className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                )}
            </button>
        </form>
    );
}
