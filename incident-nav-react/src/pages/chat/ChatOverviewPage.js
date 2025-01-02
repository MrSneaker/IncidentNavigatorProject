import { useEffect, useState } from "react";
import { FaSearch } from "react-icons/fa";
import { BiSolidMessageSquareEdit } from "react-icons/bi";
import { newChat, listChats, delChat } from "@/scripts/chat";
import { MdDeleteOutline } from "react-icons/md";
import { Link } from "react-router-dom";

const ChatOverview = () => {
    const now = new Date();
    const currentTimestamp = now.getTime();
    const [showPopup, setShowPopup] = useState(false);
    const [chatId, setChatId] = useState('');
    const [chats, setChats] = useState([]);

    function createChat() {
        newChat().then((chat) => {
            updateList();
        }).catch((error) => {
            console.error(error);
        });
    }

    function updateList() {
        listChats()?.then((chats) => {
            // order chats by date (updated_at)
            chats.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
            setChats(chats);
        }).catch((error) => {
            console.error(error);
        });
    }

    function removeChat(id) {
        delChat(id).then(() => {
            updateList();
        });
    }

    function onDeleteButtonClick(id) {
        if (showPopup) {
            removeChat(chatId);
            setChatId('');
            setShowPopup(false);
        } else {
            setShowPopup(true);
            setChatId(id);
        }
    }

    useEffect(() => {
        updateList();
    }, []);

    return (
        <div className="flex flex-col items-center justify-center h-full w-full">
            {/* Header Section */}
            <header className="chat-header">
                <h1 className="text-center font-bold dark:text-dark-accent text-light-text"
                    style={{ fontSize: 'clamp(30px, 5vw, 60px)' }}>
                    Chat Overview
                </h1>
            </header>

            {/* Description */}
            <p className="text-center text-base mt-4 max-w-2xl">
                Access your recent chats, create new ones, or search through chat history. This interface is designed to make your incident resolution journey smarter and more efficient.
            </p>

            <div className="flex flex-row mt-6">
                <button className="flex felx-col btn btn-primary p-2 px-4 m-2 gap-2 rounded-full min-w-[100px] max-w-[200px] text-center justify-center items-center font-bold border-2 border-dark-accent text-dark-accent hover:text-light-background hover:dark:text-dark-background  hover:bg-dark-accent hover:scale-110 transition-transform" onClick={createChat}>
                    New Chat <BiSolidMessageSquareEdit className="text-2xl" />
                </button>
            </div>

            <div className="container h-full bg-light-surface dark:bg-dark-surface rounded-xl p-6 mt-10 flex flex-col items-center justify-start shadow-lg drop-shadow-xl border border-black/10">
                {/* Search Bar Section */}
                <div className="p-[5px] gap-2 search-section flex flex-row w-full max-w-2xl h-[50px] shadow-md rounded-full bg-light-surface dark:bg-dark-background">
                    <input
                        type="text"
                        className="pl-[25px] w-full rounded-full bg-transparent border-gray-300 focus:border-dark-accent focus:outline-none focus:bg-light-surface dark:focus:bg-dark-surface"
                        placeholder="Search chat history..."
                    />
                    <button className="rounded-full flex items-center justify-center bg-light-accent dark:bg-dark-accent">
                        <FaSearch className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                    </button>
                </div>

                {chats.length > 0 ? (
                    <ul className="w-full max-w-2xl mt-6">
                        {chats.map((chat) => (
                            <li key={chat.id}>
                                <Link
                                    to={`/chat/${chat.id}`}
                                    className="flex flex-row justify-between items-center p-4 border border-black/10 bg-light-surface dark:bg-dark-surface hover:bg-light-accent hover:dark:bg-dark-accent hover:scale-105 hover:cursor-pointer transition-transform relative group">
                                    <h3>{chat.name || <em className="opacity-50">Untitled Chat</em>}</h3>
                                    <p className="text-sm text-light-text dark:text-dark-text/50">
                                        {
                                            (() => {
                                                const prefix = chat.updated_at === chat.created_at ? 'Created' : 'Updated';
                                                const diff = (currentTimestamp - new Date(chat.updated_at).getTime()) / 1000;

                                                const years = Math.floor(diff / (60 * 60 * 24 * 365));
                                                if (years > 0) return `${prefix} ${years} year${years > 1 ? 's' : ''} ago`;
                                                const months = Math.floor(diff / (60 * 60 * 24 * 30));
                                                if (months > 0) return `${prefix} ${months} month${months > 1 ? 's' : ''} ago`;
                                                const days = Math.floor(diff / (60 * 60 * 24));
                                                if (days > 0) return `${prefix} ${days} day${days > 1 ? 's' : ''} ago`;
                                                const hours = Math.floor(diff / (60 * 60));
                                                if (hours > 0) return `${prefix} ${hours} hour${hours > 1 ? 's' : ''} ago`;
                                                const minutes = Math.floor(diff / (60));
                                                if (minutes > 0) return `${prefix} ${minutes} minute${minutes > 1 ? 's' : ''} ago`;
                                                const seconds = Math.floor(diff);
                                                if (seconds > 0) return `${prefix} ${seconds} second${seconds > 1 ? 's' : ''} ago`;
                                                return `${prefix} just now`;
                                            })()
                                        }
                                    </p>

                                    <button
                                        className="btn btn-secondary relative right-4 opacity-0 group-hover:opacity-100 transition-opacity text-light-text dark:text-dark-text text-3xl"
                                        onClick={(ev) => {
                                            ev.preventDefault();
                                            onDeleteButtonClick(chat.id);
                                        }}>
                                        <MdDeleteOutline />
                                    </button>
                                </Link>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <div className="h-full w-full items-center justify-center flex flex-col">

                        <p className="text-light-text dark:text-dark-text/50 text-center">
                            No chats found.
                        </p>
                    </div>
                )}

            </div>
            {showPopup && (
                <div id="popup-confirm-delete" className="popup absolute z-10 w-full h-full top-0 left-0 flex items-center justify-center bg-black/50">
                    <div className="popup-content bg-light-surface dark:bg-dark-surface p-[5px] rounded-[15px] shadow-lg drop-shadow-xl border border-black/10">
                        {/* Popup Header */}
                        <div className="flex flex-row justify-between items-center">
                            <h1 className="text-center dark:text-dark-text/50 text-light-text pl-2">
                                Remove Chat
                            </h1>
                            <button
                                className="btn btn-secondary w-10 h-10 rounded-[10px] bg-transparent text-light-text dark:text-dark-text hover:bg-light-alert hover:dark:bg-dark-alert"
                                onClick={() => setShowPopup(false)}>
                                &times;
                            </button>
                        </div>

                        {/* Popup Body */}
                        <div>
                            <p className="text-center dark:text-dark-text text-light-text min-h-[100px] p-4">
                                Are you sure you want to remove this chat?
                            </p>
                        </div>

                        <div className="flex flex-row justify-end items-center">
                            <button
                                className="btn btn-primary m-2 min-w-[100px] min-h-[30px] rounded-lg bg-light-background dark:bg-dark-background text-light-text dark:text-dark-text hover:bg-light-alert hover:dark:bg-dark-alert hover:scale-105 transition-transform"
                                onClick={() => onDeleteButtonClick()}>
                                Remove
                            </button>
                            <button
                                className="btn btn-primary m-2 min-w-[100px] min-h-[30px] rounded-lg bg-light-background dark:bg-dark-background text-light-text dark:text-dark-text hover:bg-gray-300 hover:dark:bg-gray-600 hover:scale-105 transition-transform"
                                onClick={() => setShowPopup(false)}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>

    );
};

export default ChatOverview;

