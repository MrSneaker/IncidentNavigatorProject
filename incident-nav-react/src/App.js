import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { AuthProvider } from './components/auth/AuthContext';
import { logout } from './scripts/auth';

// Pages
import PrivateRoute from './components/auth/PrivateRoute';
import NotLogRoute from './components/auth/NotLogRoute';
import ChatPage from './pages/chat/ChatPage';
import ChatOverviewPage from './pages/chat/ChatOverviewPage';
import SettingsPage from './pages/SettingsPage.js';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ProfilePage from './pages/auth/ProfilePage';
import HomePage from './pages/HomePage';
import Layout from './components/layout';


function ChatRoute() {
  const query = new URLSearchParams(useLocation().search);
  const chatId = query.get('id');
  return chatId ? <ChatPage chatId={chatId} /> : <ChatOverviewPage />;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  function LogoutPage() {
    const navigate = useNavigate();

    useEffect(() => {
      logout();

      setTimeout(() => {
        navigate('/');
      }, 500);
    }, [navigate]);

    return null;
  }

  document.title = 'Incident Navigator';
  // remove tab icon
  useEffect(() => {
    const favicon = document.querySelector("link[rel='icon']");
    favicon.href = 'data:,';
  }, []);

  return (
    <Router>
      <AuthProvider isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} username={username} setUsername={setUsername}>
        <Layout isAuthenticated={isAuthenticated} username={username}>
          <Routes>
            <Route path="/" element={<HomePage isAuthenticated={isAuthenticated} />} />
            <Route path="/login" element={<NotLogRoute><LoginPage /></NotLogRoute>} />
            <Route path="/register" element={<NotLogRoute><RegisterPage /></NotLogRoute>} />
            <Route path="/profile" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
            <Route path="/chat" element={<PrivateRoute><ChatRoute /></PrivateRoute>} />
            <Route path="/logout" element={<LogoutPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
}

export default App;