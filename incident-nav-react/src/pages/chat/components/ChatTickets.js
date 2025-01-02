import React, { useEffect, useState } from 'react';
import { IoIosArrowUp, IoIosArrowDown } from "react-icons/io";



export default function ChatTickets({ listMessages, focusOn }) {
    const [listTickets, setListTickets] = useState([]);
    const [open, setOpen] = useState(false);
    const [xl, setXl] = useState(false);
    const [top, setTop] = useState(0);
    const [height, setHeight] = useState(0);
    const [width, setWidth] = useState(0);

    useEffect(() => {
        function handleResize() {
            const footer = document.querySelector('footer');
            const chat = document.getElementById('chat-container');
            // t = chat top position + chat height + 10px
            const t = chat.offsetTop;
            const h = chat.offsetHeight;
            const w = chat.offsetWidth;
            setTop(t);
            setHeight(h);
            setWidth(w);
            setXl(window.innerWidth >= 1280);
        }
        window.addEventListener('resize', handleResize);
        handleResize();

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        if (focusOn < 0){
            setListTickets([])
        }
        const list =  listMessages[focusOn]?.parts.references
        if (!list){
            setListTickets([])
        } else {
            setListTickets(list)
        }
    }, [focusOn, listMessages])

    return (
        <div
            className="relative xl:fixed overflow-y-auto rounded-3xl flex flex-col items-center justify-start gap-2 p-2 transition-all duration-300"
            style={{
                top: xl ? top + 'px' : '0',
                height: xl ? height + 'px' : 'auto',
                width: xl ? window.innerWidth / 2 - width / 2 - 20 + 'px' : '100%',
                left: xl ? '10px' : '0',
                backgroundColor: `rgba(0, 0, 0, ${open | xl ? 0.1 : 0})`,
            }}>
            <button
                onClick={() => setOpen(!open)}
                className='xl:hidden flex justify-center text-xl bg-white/10 w-[100px] rounded-full p-1'
            >
                {!open ? <IoIosArrowUp /> : <IoIosArrowDown />}
            </button>
            <div className='hidden xl:flex justify-start items-center font-bold p-2 px-6'>
                Tickets :
            </div>

            <div
                className="overflow-y-auto translate-all duration-300 w-full"
                style={{ height: xl ? 'auto' : open ? height / 2 + 'px' : '0' }}
            >
                <ul className='flex flex-wrap w-full gap-2 '>
                    {
                       listTickets.map((ticket, index) => (
                            <li
                                key={index}
                                className='flex flex-col items-start justify-start gap-2 p-2 rounded-lg bg-black/10 w-max-[200px] w-full'
                                style={{ maxWidth: width / 2 - 20 + 'px'}}
                            >
                                {/* Header */}
                                <div
                                    className='flex flex-row items-start justify-start gap-2 w-full'
                                    style={{ color: ticket.color }}
                                >
                                    <span className='font-bold'>#{ticket.accident_id}</span>
                                    <span className='font-bold w-full'>{ticket.event_type}</span>
                                </div>
                                <hr className='w-full border-t border-gray-300 opacity-30' />
                                {/* Body */}
                                <div className='flex flex-col items-start justify-start gap-2 w-full'>
                                    <span>{ticket.accident_title}</span>
                                </div>
                                {/* Footer */}
                                <div>
                                    <span className='font-italic'>
                                        Industry: {ticket.industry_type}
                                    </span>
                                </div>
                            </li>
                        ))
                    }

                </ul>

            </div>
        </div>
    )
}