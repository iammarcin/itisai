// App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { StateContextProvider } from "./components/StateContextProvider";
import Main from './components/Main';
import Login from './components/Login';
import Health from './components/health/Health';
import Garmin from './components/Garmin';
import PrivacyPolicy from './components/Privacy';
import TermsAndConditions from './components/TermsConditions';

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

    if (isTokenValid(tokenData)) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <StateContextProvider>
      <Router>
        <Routes>
          {isAuthenticated ? (
            <>
              <Route path="/" element={<Main />} />
              <Route path="/session/:sessionId" element={<Main />} />
              <Route path="/health" element={<Health />} />
              <Route path="/garmin" element={<Garmin />} />
            </>
          ) : (
            <Route path="/" element={<Login onLoginSuccess={handleLoginSuccess} />} />
          )}
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsAndConditions />} />
        </Routes>
      </Router>
    </StateContextProvider>
  );
}

export default App;
