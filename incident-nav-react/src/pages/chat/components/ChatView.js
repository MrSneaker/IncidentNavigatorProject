import { useEffect, useState } from "react";
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { IoIosCloseCircle } from "react-icons/io";


function getColorRGB(color) {
    let tempDiv = document.createElement('div');
    tempDiv.style.color = color;
    document.body.appendChild(tempDiv);

    // Get the color in RGB
    let colorRGB = window.getComputedStyle(tempDiv).color;

    // Remove the temp div
    document.body.removeChild(tempDiv);

    // Parse the RGB color
    let rgb = colorRGB.match(/\d+/g).map(Number);
    return { r: rgb[0], g: rgb[1], b: rgb[2] };
}

function changeColor(text) {
    let newText = text;
    console.log(text);
    const tags = text.match(/<[^>]*>.+?<\/[^>]*>/g);
    if (tags) {
        tags.forEach(tag => {
            const content = tag.match(/<[^>]*>(.+?)<\/[^>]*>/).pop();
            const color = tag.match(/style=['"][^'"]*color:\s*([^;'"]+)/)?.[1];
            const rgb = getColorRGB(color);
            // Black or white text
            if ((rgb.r === 255 && rgb.g === 255 && rgb.b === 255) || (rgb.r === 0 && rgb.g === 0 && rgb.b === 0)) {
                newText = newText.replace(tag, `<span class="text-light-text dark:text-dark-text">${content}</span>`);
            }
            else {
                // keep the color but set font weight to bold
                newText = newText.replace(tag, `<span style="color: ${color}; font-weight: bold;">${content}</span>`);

            }



        });
    }
    return newText;
}

function Markdown({ children, ...props }) {
    const content = changeColor(children)
    return <ReactMarkdown rehypePlugins={[rehypeRaw]} {...props}>{content}</ReactMarkdown>
}

export default function ChatView({ listMessages, setFocusOn, ...props }) {
    const [focusIndex, setFocusIndex] = useState(0);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isOnBottom, setIsOnBottom] = useState(true);
    const properties = {
        ...props,
        className: "flex flex-col w-full h-full overflow-y-auto" + (props.className ? ` ${props.className}` : ''),
        id: "chat-view"
    }

    useEffect(() => {
        setFocusOn(focusIndex);
    }, [focusIndex, setFocusOn])

    function handleResize(event) {
        const chat = document.getElementById('chat-view');
        if (chat) {
            chat.scrollTop = chat.scrollHeight;
            setMousePosition({ x: event[0].contentRect.x, y: event[0].contentRect.y });
        }
    }

    function searchNearestMessage(y) {
        const chat = document.querySelector('#chat-view');
        const messages = chat.querySelectorAll('.message');
        let minDistance = Number.MAX_VALUE;
        let index = -1;

        messages.forEach((message, i) => {
            if (message.getAttribute("class").includes('user-message')) {
                return;
            }
            const clientY = message.getBoundingClientRect().top - chat.getBoundingClientRect().top;
            if (clientY < message.clientH) {
                return;
            }
            const distance = Math.abs(clientY - y);
            if (distance < minDistance) {
                minDistance = distance;
                index = i;
            }
        });

        setFocusIndex(index);
    }

    function onScroll(event) {
        searchNearestMessage(mousePosition.y);
        setIsOnBottom(event.target.scrollHeight - event.target.scrollTop === event.target.clientHeight);
    }

    function onMouseMove(event) {
        const chat = document.getElementById('chat-view');
        const rect = chat.getBoundingClientRect();
        setMousePosition({ x: event.clientX - rect.x, y: event.clientY - rect.y });
    }

    function onMouseLeave(event) {
        setFocusIndex(listMessages.length - 1);
    }

    useEffect(() => {
        searchNearestMessage(mousePosition.y);
    }, [mousePosition]);

    function scrollToBottom() {
        const chat = document.getElementById('chat-view');
        if (chat) {
            chat.scrollTop = chat.scrollHeight;
        }
    }

    useEffect(() => {
        // Resize observer to scroll to the bottom of the chat
        const chat = document.getElementById('chat-view');
        const resizeObserver = new ResizeObserver(handleResize);
        resizeObserver.observe(chat);
        // Scroll observer to focus on the nearest message
        chat.addEventListener('scroll', onScroll);
        scrollToBottom();

        // Mouse move event listener
        chat.addEventListener('mousemove', onMouseMove);
        // Mouse leave event listener
        chat.addEventListener('leave', onMouseLeave);

        return () => {
            resizeObserver.disconnect();
            chat.removeEventListener('scroll', onScroll);
            chat.removeEventListener('mousemove', onMouseMove);
            chat.removeEventListener('leave', onMouseLeave);

        }
    }, []);

    useEffect(() => {
        if (isOnBottom) {
            scrollToBottom();
        }
    }, [listMessages, isOnBottom]);

    return (
        <div {...properties}>
            {listMessages.map((message, index) => (
                <div key={index} className="flex flex-row items-center justify-start gap-2">
                    {message.source === 'user' ? (
                        <div className="message user-message flex flex-row w-full items-end justify-end gap-2" key={index}>
                            <div className="p-2 px-[20px] m-1 min-w-[40px] max-w-[90%] md:max-w-[80%] rounded-3xl rounded-br-none bg-dark-accent text-light-surface break-words">
                                <Markdown>{message.parts.answer}</Markdown>
                            </div>
                        </div>
                    ) : (
                        <div className="message model-message w-full items-start justify-start gap-2" >
                            <div className="flex flex-row p-2 gap-2 m-1">

                                <div className=" h-auto bg-black/20 dark:bg-white/20 transition-width rounded-3xl duration-200 ease-in-out" style={{ width: index === focusIndex && message.status === 1 ? '8px' : '0px' }}></div>
                                {
                                    message.status === -1 && (
                                        <IoIosCloseCircle className="w-6 h-6 text-red-500" />
                                    )
                                }
                                <div className="max-w-[90%] ">

                                    {message.status === 0 ? (
                                        <div className="flex items-center gap-2">
                                            <div className="w-6 h-6 border-4 border-t-transparent border-dark-accent rounded-full animate-spin"></div>
                                            <span className="text-light-text/50 dark:text-dark-text/50">Responding...</span>
                                        </div>
                                    ) : (
                                        <Markdown className="text-left">
                                            {message.parts.answer}
                                        </Markdown>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    )
}