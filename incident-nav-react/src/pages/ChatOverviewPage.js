import { FaSearch } from "react-icons/fa";
import { BiSolidMessageSquareEdit } from "react-icons/bi";

const ChatOverview = () => {

    function createChat() {
        console.log("Creating a new chat...");
    }

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
                <button className="flex felx-col btn btn-primary p-2 px-4 m-2 gap-2 rounded-full min-w-[100px] max-w-[200px] text-center justify-center items-center font-bold border-2 border-dark-accent text-dark-accent hover:text-dark-background hover:bg-dark-accent hover:scale-110 transition-transform" onClick={createChat}>
                    New Chat <BiSolidMessageSquareEdit className="text-2xl" />
                </button>
            </div>

            <div className="container h-full bg-light-surface dark:bg-dark-surface rounded-xl p-6 mt-10 flex flex-col items-center justify-start shadow-lg drop-shadow-xl border border-black/10">
                {/* Search Bar Section */}
                <div className="p-[5px] gap-2 search-section flex flex-row w-full max-w-2xl h-[50px] shadow-md rounded-full bg-light-surface dark:bg-dark-background">
                    <input
                        type="text"
                        className="pl-[25px] w-full rounded-full bg-transparent border-gray-300 focus:border-dark-accent focus:outline-none"
                        placeholder="Search chat history..."
                    />
                    <button className=" rounded-full flex items-center justify-center bg-light-accent dark:bg-dark-accent">
                        <FaSearch className="text-light-surface dark:text-dark-surface w-[40px] h-[40px] p-[10px]" />
                    </button>
                </div>

                {/* Placeholder Message for Non-Functional Search */}
                <div className="search-placeholder mt-10 h-full flex flex-col items-center justify-center">
                    <p className="text-center text-gray-500 text-lg">Not Available</p>
                </div>

            </div>

        </div>
    );
};

export default ChatOverview;

