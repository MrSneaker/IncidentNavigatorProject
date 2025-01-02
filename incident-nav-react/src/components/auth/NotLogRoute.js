import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const NotLogRoute = ({ children }) => {
  const { user } = useContext(AuthContext);
  if (!user) {
    return children;
  }
  return <Navigate to="/" />; 
};

export default NotLogRoute;
