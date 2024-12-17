import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import ChatPage from './pages/ChatPage';
import ChatOverviewPage from './pages/ChatOverviewPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import HomePage from './pages/HomePage';

import Layout from './Layout';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function App() {
  localStorage.setItem('authToken', 'fake-auth-token');
  localStorage.setItem('username', 'fake-username');

  function LogoutPage() {
    const navigate = useNavigate();
    

    useEffect(() => {
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      

      navigate('/login');
    }, [navigate]);

    return null;
  }

  return (
    <Router>
      <Layout>
        <Routes>

          {/* Home */}
          <Route path="/" element={<HomePage/>} />

          {/* User */}
          <Route path="/register" element={<RegisterPage/>} />
          <Route path="/login" element={<LoginPage/>} />
          <Route path="/logout" element={<LogoutPage />} />

          {/* Profile */}
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage/>
            </ProtectedRoute>
          } />

          {/* Chat */}
          <Route path="/chat" element={
            <ProtectedRoute>
              <ChatOverviewPage/>
            </ProtectedRoute>
          } />
          <Route path="/chat/:chatId" element={
            <ProtectedRoute>
              <ChatPage/>
            </ProtectedRoute>
          } />

        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

