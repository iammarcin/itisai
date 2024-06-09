// App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './components/Login';

/*
expirationDate.setDate(expirationDate.getDate() + 15);
localStorage.setItem('authToken', JSON.stringify({
  token: response.message.result.token,
  expiration: expirationDate.toISOString(),
}));*/

const isTokenValid = (tokenData) => {
  if (!tokenData || !tokenData.expiration) {
    return false;
  }
  const now = new Date();
  const expirationDate = new Date(tokenData.expiration);
  return now < expirationDate;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if the user is already authenticated
    const tokenData = JSON.parse(localStorage.getItem('authToken'));
    console.log("tokenData : ", tokenData);
    if (isTokenValid(tokenData)) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        {isAuthenticated ? (
          <Route path="/" element={<Layout />} />
        ) : (
          <Route path="/" element={<Login onLoginSuccess={handleLoginSuccess} />} />
        )}
      </Routes>
    </Router>
  );
}

export default App;
