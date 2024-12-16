import React from 'react';
import NotLoggedPage from '../pages/NotLoggedPage';

const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem('authToken'); // On récupère le token du localStorage
    console.log(isAuthenticated);
    if (!isAuthenticated) {
        return <NotLoggedPage />; // Redirection vers la page de connexion
    }

    return children; // Accès au contenu protégé
};

export default ProtectedRoute;
