import React, {useEffect, useState} from 'react';
import NavBar from './NavBar';
import MobileNavBar from './MoblieNavBar';

const Header = ({ navLinks }) => {
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
            <h1>Incident Navigation</h1>
            {isMobile ? (
                <MobileNavBar navLinks={navLinks}/>
            ) : (
                <NavBar navLinks={navLinks}/>
            )}
        </header>
    );
};

export default Header;