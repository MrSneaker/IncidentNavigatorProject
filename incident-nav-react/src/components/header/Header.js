import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import NavBar from './NavBar';
import MobileNavBar from './MoblieNavBar';

const Header = ({ navLinks, isAuthenticated, username }) => {
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkIsMobile = () => {
            if (window.innerWidth <= 768) {
                setIsMobile(true);
            } else {
                setIsMobile(false);
            }
        };

        checkIsMobile();
        window.addEventListener('resize', checkIsMobile);

        return () => {
            window.removeEventListener('resize', checkIsMobile);
        };
    }, []);

    return (
        <header className="p-4 flex justify-between items-center dark:bg-dark-background bg-light-background">
            <Link to="/" className="text-2xl font-bold dark:text-dark-text text-light-text">Incident Navigator</Link>
            {isMobile ? (
                <MobileNavBar navLinks={navLinks} isAuthenticated={isAuthenticated} username={username} />
            ) : (
                <NavBar navLinks={navLinks} isAuthenticated={isAuthenticated} username={username} />
            )}
        </header>
    );
};

export default Header;