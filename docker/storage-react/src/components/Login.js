// Login.js
import React, { useState } from 'react';
import apiService from '../services/apiService';
import './Login.css'; // Assuming you have CSS for login

const Login = ({ onLoginSuccess }) => {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    console.log("Login.js: handleLogin")
    e.preventDefault();
    try {
      const response = await apiService.authUser(user, password);
      console.log("Login.js: handleLogin: response", response)
      if (response && response.result && response.status !== 'fail') {
        const expirationDate = new Date();
        expirationDate.setDate(expirationDate.getDate() + 15);
        localStorage.setItem('authToken', JSON.stringify({
          token: response.result.token,
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
