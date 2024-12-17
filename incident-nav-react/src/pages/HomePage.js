import { GoArrowUpRight } from "react-icons/go";
import { Link } from "react-router-dom";

export default function HomePage({ isAuthenticated }) { 
    return (
      <div className="flex flex-col items-center justify-center h-full w-full"> 
        <h1 className="text-center font-bold dark:text-dark-accent text-light-text"
            style={{ fontSize: 'clamp(30px, 5vw, 60px)' }}>
            Welcome to Incident Navigator
        </h1>
        <p className="text-center text-base mt-4 max-w-2xl">
            Discover smarter, faster incident resolution with IncidentNavigator. Our system combines Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to offer dynamic, interactive, and traceable incident support.
        </p>        

        {!isAuthenticated ? (
            <div className="flex flex-row mt-6">
                <Link to='/login' className="btn btn-primary m-2 rounded-full p-2 min-w-[100px] max-w-[200px] text-center font-bold border-2 border-dark-accent text-dark-accent hover:text-dark-background hover:bg-dark-accent hover:scale-110 transition-transform">
                    Login
                </Link>
                <Link to='/register' className="btn btn-primary m-2 rounded-full p-2 min-w-[100px] max-w-[200px] text-center font-bold border-2 border-dark-accent text-dark-accent hover:text-dark-background hover:bg-dark-accent hover:scale-110 transition-transform">
                    Register
                </Link>
            </div>
        ) : (
            <Link to="/chat" className="btn btn-secondary m-2 rounded-full bg-gradient-to-r text-center from-dark-accent to-light-accent p-2 min-w-[100px] max-w-[200px] hover:scale-105 transition-transform flex px-4 py-2 items-center">
                Start Chatting <GoArrowUpRight className="text-2xl ml-2" />
            </Link>
        )}
      </div>
    );
};