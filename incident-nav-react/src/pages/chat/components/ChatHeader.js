import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiEdit } from 'react-icons/fi';
import { IoMdArrowBack } from 'react-icons/io';


export default function ChatHeader({ chatName, setChatName, renameError, loading }) {
    const [currentChatName, setCurrentChatName] = useState(chatName);

    useEffect(() => {
        setCurrentChatName(chatName);
    }, [chatName]);

    return (
        <div className="flex items-center justify-between w-full p-2 gap-4">
            <Link to="/chat" className="text-2xl font-bold"> <IoMdArrowBack /> </Link>
            <div className="relative text-2xl font-bold w-full flex flex-col items-center justify-center">
                {!loading && (
                    <>
                        <div className='w-full h-full flex items-center justify-center max-w-[400px]'>
                            <input
                                type="text"
                                className="bg-transparent p-2 m-0 text-2xl font-bold rounded-lg text-center border border-transparent hover:border-light-background hover:dark:border-dark-background focus:border-light-accent focus:dark:border-light-accent outline-none hover:bg-black/2"
                                value={currentChatName}
                                placeholder="Untitled Chat"
                                onFocus={(e) => e.target.nextSibling.style.display = 'none'}
                                onBlur={(e) => {
                                    e.target.nextSibling.style.display = 'block'
                                    if (chatName !== currentChatName) {
                                        setChatName(currentChatName);
                                    }
                                }}
                                onChange={(e) => setCurrentChatName(e.target.value)}
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
                        {
                            renameError && (
                                <p className="text-light-alert dark:text-dark-alert text-sm font-normal">
                                    {renameError}
                                </p>
                            )
                        }
                    </>
                )
                }
            </div>
        </div>
    )
}