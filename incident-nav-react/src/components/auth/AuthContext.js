import React, { createContext, useState, useEffect } from 'react';
import { getCurrent, logout } from '../../scripts/auth';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();

export const AuthProvider = ({ children , isAuthenticated, setIsAuthenticated, username, setUsername }) => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    async function fetchUser() {
        const response = await getCurrent();
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
    }
    
    useEffect(() => {
        fetchUser();
    }, [navigate]);

    return (
        <AuthContext.Provider value={{ user, setUser, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
