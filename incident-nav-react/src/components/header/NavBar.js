import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const NavBar = ({ navLinks }) => {
    const location = useLocation();

    return (
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
    );
};

export default NavBar;