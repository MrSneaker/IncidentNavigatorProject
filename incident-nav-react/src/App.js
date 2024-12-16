import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';


function App() {
  return (
    <Router>
      <Routes>

        {/* Home */}
        <Route path="/" element={
          <h1>Accueil</h1>
        } />

        {/* User */}
        <Route path="/register" element={
          <h1>Inscription</h1>
        } />
        <Route path="/login" element={
          <h1>Connexion</h1>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <h1>Profil</h1>
          </ProtectedRoute>
        } />

        {/* Chat */}
        <Route path="/chat" element={
          <ProtectedRoute>
            <h1>Historique des chats</h1>
          </ProtectedRoute>
        } />
        <Route path="/chat/:chatId" element={
          <ProtectedRoute>
            <h1>Chat</h1>
          </ProtectedRoute>
        } />

      </Routes>
    </Router>
  );
}

export default App;
