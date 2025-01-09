import React from 'react';

const NotLoggedPage = () => {
    return (
        <div>
            <h1>Not Logged In</h1>
            <p>Please log in to view this page.</p>
            <div>
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            </div>
        </div>
    );
};

export default NotLoggedPage;