import React, { createContext, useState, useEffect } from 'react';
import { getCurrent } from '@/scripts/auth';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children , isAuthenticated, setIsAuthenticated, username, setUsername }) => {
    const navigate = useNavigate();
    const [requested, setRequested] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        getCurrent().then((response) => {
            if (response.error) {
                setUser(null);
                setIsAuthenticated(false);
                setUsername('');
            } else {
                const user = response.data;
                setUser(user);
                setIsAuthenticated(true);
                setUsername(user.username);
            }
            setRequested(true);
        });
    }, [navigate, setIsAuthenticated, setUsername]);

    return (
        <AuthContext.Provider value={{ user, setUser, isAuthenticated, setIsAuthenticated, username, setUsername }}>
            {requested ? children : null}
        </AuthContext.Provider>
    );
};
