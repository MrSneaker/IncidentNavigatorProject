import React from 'react';
import Header from './components/header/Header';
import Footer from './components/footer/Footer';

const Layout = ({ children }) => {
    const navLinks = [
        { path: '/', label: 'Home', visibleWhenLoggedIn: 0, enabledWhenLoggedIn: 0 },
        { path: '/chat', label: 'Chat', visibleWhenLoggedIn: 1, enabledWhenLoggedIn: 1 },
    ];

    return (
        <div className="flex flex-col h-screen dark:text-dark-text text-light-text">
            <Header navLinks={navLinks}/>
            <main className="flex p-4 overflow-auto h-[100%] dark:bg-dark-surface bg-light-surface">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;