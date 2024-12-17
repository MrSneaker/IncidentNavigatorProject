import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaUserCircle } from 'react-icons/fa';

const NavBar = ({ navLinks, isAuthenticated, username }) => {
    const location = useLocation();
    const [showDropdown, setShowDropdown] = useState(false);

    // Close dropdown when clicking outside
    React.useEffect(() => {
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
        <nav className="flex justify-between items-center gap-4">
            <ul className="flex space-x-4">
                {navLinks.map((link) => (
                    (link.auth === isAuthenticated || link.auth === null) && link.path !== '/profile' ? (
                        <li key={link.path}>
                            <Link
                                to={link.path}
                                className={`${location.pathname === link.path ? 'underline dark:text-dark-accent text-light-accent' : 'dark:text-dark-text text-light-text'} text-xl`}
                            >
                                {link.label}
                            </Link>
                        </li>
                    ) : null
                ))}
            </ul>
            {isAuthenticated && (
                <div className="relative flex items-center dropdown" onClick={() => setShowDropdown(!showDropdown)}>
                    <button className="bg-light-surface dark:bg-dark-surface hover:dark:bg-dark-accent hover:bg-light-accent dark:text-dark-text text-light-text text-2xl ml-4 flex items-center gap-4 p-0 pl-4 rounded-full h-12 justify-center" onClick={() => setShowDropdown(!showDropdown)}>
                        <span className="hidden sm:inline text-md">
                            {username}
                        </span>
                        <FaUserCircle className="mr-2 text-3xl" />
                    </button>
                    <div className="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-dark-surface rounded-md shadow-xl p-1" style={{ display: showDropdown ? 'block' : 'none' }}>
                        <Link
                            to="/profile"
                            className="block px-4 py-2 rounded-md text-xl text-light-text dark:text-dark-text hover:bg-light-background dark:hover:bg-dark-background">
                            Profile
                        </Link>
                        <Link to="/logout" className="block px-4 py-2 rounded-md text-xl text-light-text dark:text-dark-text hover:bg-light-background dark:hover:bg-dark-background">
                            Disconnect
                        </Link>
                    </div>
                </div>
            )}
        </nav>
    );
};

export default NavBar;