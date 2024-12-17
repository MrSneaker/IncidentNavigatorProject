import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { GoSignOut } from 'react-icons/go';

const MobileNavBar = ({ navLinks, isAuthenticated, username }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const location = useLocation();

    const toggleNavBar = () => {
        setIsOpen(!isOpen);
    };

    function handleLogout() {
        // logout logic
    }

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (showDropdown && !event.target.closest('.dropdown')) {
                setShowDropdown(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showDropdown]);

    return (
        <div>
            <button onClick={toggleNavBar} className="burger-button">
                ☰
            </button>
            <div
                className={`fixed top-0 right-0 h-full w-full bg-dark-background/80 shadow-md transition-transform duration-300 backdrop-blur-sm ${
                    isOpen ? 'transform translate-x-0' : 'transform translate-x-full'
                }`}
            >
                <button onClick={toggleNavBar} className="close-button absolute top-4 right-4 text-white text-3xl">
                    &times;
                </button>
                <nav className="flex justify-center w-full h-full items-center">
                    <ul className="flex flex-col space-y-4 p-4 gap-4 color-white text-2xl text-center">
                        {navLinks.map((link) => (
                            link.auth === null || link.auth === isAuthenticated ? (
                                <li key={link.path}>
                                    <Link
                                        to={link.path}
                                        className={`${location.pathname === link.path ? 'underline dark:text-dark-accent text-light-accent' : 'text-dark-text'}`}
                                        onClick={toggleNavBar}
                                    >
                                        {link.label}
                                    </Link>
                                </li>
                            ) : null
                        ))}
                        
                    </ul>
                </nav>
                {isAuthenticated && (
                <div className="absolute bottom-4 right-4 flex items-center space-x-2">
                    <GoSignOut className="text-white text-xl" />
                    <Link to="/logout" className="text-white" onClick={handleLogout}>
                        Logout
                    </Link>
                </div>
            )}
            </div>
            
        </div>
    );
};

export default MobileNavBar;