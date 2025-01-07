import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { AuthProvider } from './components/auth/AuthContext';
import { logout, getCurrent } from './scripts/auth';

// Pages
import PrivateRoute from './components/auth/PrivateRoute';
import NotLogRoute from './components/auth/NotLogRoute';
import ChatPage from './pages/chat/ChatPage';
import ChatOverviewPage from './pages/chat/ChatOverviewPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import HomePage from './pages/HomePage';
import Layout from './components/layout';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  function LogoutPage() {
    const navigate = useNavigate();

    useEffect(() => {
      const response = logout();
      console.log(response);

      setTimeout(() => {
        navigate('/');
      }, 1000);
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
      <Layout isAuthenticated={isAuthenticated} username={username}>
        <AuthProvider isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} username={username} setUsername={setUsername}>
          <Routes>
            <Route path="/" element={<HomePage isAuthenticated={isAuthenticated} />} />
            <Route path="/login" element={<NotLogRoute><LoginPage /></NotLogRoute>} />
            <Route path="/register" element={<NotLogRoute><RegisterPage /></NotLogRoute>} />
            <Route path="/profile" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
            <Route path="/chat/:id" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
            <Route path="/chat" element={<PrivateRoute><ChatOverviewPage /></PrivateRoute>} />
            <Route path="/logout" element={<LogoutPage />} />
          </Routes>
        </AuthProvider>
      </Layout>
    </Router>
  );
}

export default App;