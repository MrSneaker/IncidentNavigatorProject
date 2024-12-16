import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem('authToken'); // On récupère le token du localStorage
    console.log(isAuthenticated);
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />; // Redirection vers la page de connexion
    }

    return children; // Accès au contenu protégé
};

export default ProtectedRoute;
