// Login.js
import React, { useState } from 'react';
import apiService from '../services/apiService';
import './Login.css';

const Login = ({ onLoginSuccess }) => {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const userInput = { "username": user, "password": password };
      const response = await apiService.triggerDBRequest("db", "db_auth_user", userInput);

      if (response.message && response.message.result && response.code === 200) {
        const expirationDate = new Date();
        expirationDate.setDate(expirationDate.getDate() + 15);

        localStorage.setItem('authToken', JSON.stringify({
          token: response.message.result.token, // TODO - one day real token here
          expiration: expirationDate.toISOString(),
        }));
        onLoginSuccess();
      } else {
        setError('Invalid username or password');
      }
    } catch (error) {
      setError('Failed to authenticate');
    }
  };

  return (
    <div className="login">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>Username:</label>
          <input type="text" value={user} onChange={(e) => setUser(e.target.value)} />
        </div>
        <div>
          <label>Password:</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit">Login</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
};

export default Login;
