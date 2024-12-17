import React from 'react';
import Header from './components/header/Header';
import Footer from './components/footer/Footer';

const Layout = ({ children, isAuthenticated, username }) => {
    const navLinks = [
        { path: '/', label: 'Home', auth: null },
        { path: '/chat', label: 'Chat', auth: true },
        { path: '/login', label: 'Login', auth: false },
        { path: '/register', label: 'Register', auth: false },
        { path: '/profile', label: 'Profile', auth: true },
    ];

    return (
        <div className="flex flex-col h-screen dark:text-dark-text text-light-text">
            <Header navLinks={navLinks} isAuthenticated={isAuthenticated} username={username} />
            <main className="flex p-4 overflow-auto h-[100%] dark:bg-dark-surface bg-light-surface">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;