import React, { createContext, useState, useEffect } from 'react';
import { getCurrent } from '@/scripts/auth';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children , isAuthenticated, setIsAuthenticated, username, setUsername }) => {
    const navigate = useNavigate();
    const [requested, setRequested] = useState(false);
    const [user, setUser] = useState(null);
    const [isAdmin, setIsAdmin] = useState(false);

    async function fetchUser() {
        const response = await getCurrent();
        if (response.error) {
            setUser(null);
            setIsAuthenticated(false);
            setUsername('');
            setIsAdmin(false);
        } else {
            const user = response.data;
            setUser(user);
            setIsAuthenticated(true);
            setUsername(user.username);
            setIsAdmin(user.isAdmin)
        }
        setRequested(true);
    }
    
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
        <AuthContext.Provider value={{ user, setUser, isAuthenticated, setIsAuthenticated, username, setUsername, isAdmin}}>
            {requested ? children : null}
        </AuthContext.Provider>
    );
};
