import React from 'react';
import { Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';


const Layout = ({ children }) => {
    const location = useLocation();
    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/chat', label: 'Chat' },
        { path: '/profile', label: 'Profile' }
    ];

    return (
        <div className="flex flex-col h-screen">
            <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
                <h1>Incident Navigation</h1>
                <nav>
                    <ul className="flex space-x-4">
                        {navLinks.map((link) => (
                            <li key={link.path}>
                                <Link 
                                    to={link.path} 
                                    className={`${location.pathname === link.path ? 'underline' : ''} min-w-[100px]`}
                                >
                                    {link.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>
            </header>
            <main className="flex p-4 overflow-auto h-[100%]">
                {children}
            </main>
            <footer className="bg-gray-800 text-white p-4">
                &copy; 2024 Incident Navigation
            </footer>
        </div>
    );
};

export default Layout;