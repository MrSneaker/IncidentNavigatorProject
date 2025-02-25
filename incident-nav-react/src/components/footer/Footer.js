import React from 'react';
import ThemeToggle from './ThemeToggle';

const Footer = () => {
    return (
        <footer className="p-3 flex justify-between items-center dark:bg-dark-surface bg-light-surface dark:text-dark-text text-light-text">
            &copy; 2024 Incident Navigation

            <ThemeToggle />
        </footer>
    );
};

export default Footer;