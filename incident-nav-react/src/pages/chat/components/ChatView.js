import { useEffect, useState } from "react";
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

function Markdown({ children }) {
    return <ReactMarkdown rehypePlugins={[rehypeRaw]}>{children}</ReactMarkdown>
}

export default function ChatView({ listMessages, setFocusOn, ...props }) {
    const [lastVisibleIndex, setLastVisibleIndex] = useState(0);
    const properties = {
        ...props,
        className: "flex flex-col w-full h-full overflow-y-auto " + (props.className ? ` ${props.className}` : ''),
        id: "chat-view"
    }

    function handleResize() {
        const chat = document.getElementById('chat-view');
        if (chat){
            chat.scrollTop = chat.scrollHeight;
            searchLastVisibleIndex();
        }
    }

    function searchLastVisibleIndex() {
        // get the chat view
        const chat = document.querySelector('#chat-view');
        const messages = chat.querySelectorAll('.message');
        setLastVisibleIndex(-1);

        if (chat.scrollHeight - chat.scrollTop === chat.clientHeight) {
            setLastVisibleIndex(messages.length - 1);
            return lastVisibleIndex;
        }

        let minDistance = chat.clientHeight;
        for (let i = 0; i < messages.length; i++) {
            const message = messages[i];
            if (message.classList.contains('model-message')) {
                const rect = message.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                const distCenter = Math.abs(rect.top + rect.height / 2 - window.innerHeight / 2);

                if (isVisible && distCenter < minDistance) {
                    minDistance = distCenter;
                    setLastVisibleIndex(i);
                }
            }
        }
        return lastVisibleIndex;
    }

    useEffect(() => {
        setFocusOn(lastVisibleIndex);
    }, [lastVisibleIndex])

    function onScroll() {
        searchLastVisibleIndex();
    }

    useEffect(() => {
        const chat = document.querySelector('#chat-view');
        const resizeObserver = new ResizeObserver(handleResize);
        resizeObserver.observe(chat);
        chat.addEventListener('scroll', onScroll);
        return () => {
            resizeObserver.disconnect();
            chat.removeEventListener('scroll', onScroll);
        }
    }, []);

    useEffect(() => {
        const chat = document.querySelector('#chat-view');
        chat.scrollTop = chat.scrollHeight;
        searchLastVisibleIndex();
    }, [listMessages]);

    return (
        <div {...properties}>
            {listMessages.map((message, index) => (
                <div key={index} className="flex flex-row items-center justify-start gap-2">
                    {message.source === 'user' ? (
                        <div className="message user-message flex flex-row w-full items-end justify-end gap-2">
                            <div className="p-2 px-[20px] m-1 min-w-[40px] max-w-[90%] md:max-w-[80%] rounded-3xl rounded-br-none bg-dark-accent text-light-surface break-words">
                                <Markdown>{message.parts.answer}</Markdown>
                            </div>
                        </div>
                    ) : (
                        <div className="message model-message flex flex-row w-full items-start justify-start gap-2">
                            <div className="p-4 px-[20px] min-w-[40px] max-w-[90%] md:max-w-[80%] m-1 rounded-3xl rounded-bl-none break-words transition-background-color duration-300"
                                style={{ backgroundColor: index === lastVisibleIndex ? `rgba(0, 0, 0, 0.2)` : 'transparent' }}
                            >
                                {message.status === 0 ? (
                                    <div className="flex items-center gap-2">
                                        <div className="border-t-transparent border-solid border-2 rounded-full p-2 w-4 h-4 animate-spin border-light-accent bg-transparent"
                                        />
                                        <span className="text-light-text/50 dark:text-dark-text/50">Responding...</span>
                                    </div>
                                ) : (
                                    <Markdown className="text-left">
                                        {message.parts.answer}
                                    </Markdown>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    )
}