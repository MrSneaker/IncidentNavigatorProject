import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

const MobileNavBar = ({ navLinks }) => {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    const toggleNavBar = () => {
        setIsOpen(!isOpen);
    };

    return (
        <div>
            <button onClick={toggleNavBar} className="burger-button">
                ☰
            </button>
            <div
                className={`fixed top-0 right-0 h-full w-full bg-black/80 shadow-md transition-transform duration-300 ${
                    isOpen ? 'transform translate-x-0' : 'transform translate-x-full'
                }`}
            >
                <button onClick={toggleNavBar} className="close-button absolute top-4 right-4 text-white text-3xl">
                    &times;
                </button>
                <nav className="flex justify-center w-full h-full items-center">
                    <ul className="flex flex-col space-y-4 p-4 gap-4 color-white text-2xl text-center">
                        {navLinks.map((link) => (
                            <li key={link.path}>
                                <Link
                                    to={link.path}
                                    className={`${location.pathname === link.path ? 'underline text-accent text-bold' : 'text-white'} min-w-[100px]`}
                                    onClick={toggleNavBar}
                                >
                                    {link.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>
            </div>
        </div>
    );
};

export default MobileNavBar;