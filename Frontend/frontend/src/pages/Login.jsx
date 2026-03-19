import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import BACKEND from "../config";
import "../css/Auth.css";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!username || !password) { setError('Username and password are required'); return; }
        setLoading(true);
        const formDetails = new URLSearchParams();
        formDetails.append('username', username);
        formDetails.append('password', password);
        try {
            const response = await fetch(`${BACKEND}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formDetails,
            });
            setLoading(false);
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('username', username);
                window.dispatchEvent(new Event('login'));
                navigate('/protected');
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Login failed');
            }
        } catch {
            setLoading(false);
            setError('An error occurred. Please try again.');
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-logo">RIDEXA</div>
                <p className="auth-subtitle">Sign in to your account</p>
                <form onSubmit={handleSubmit}>
                    <div className="auth-field">
                        <label>Username</label>
                        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" />
                    </div>
                    <div className="auth-field">
                        <label>Password</label>
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" />
                    </div>
                    {error && <p className="auth-error">{error}</p>}
                    <button className="auth-btn" type="submit" disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>
                <p className="auth-footer">Don't have an account? <Link to="/register">Register</Link></p>
            </div>
        </div>
    );
}

export default Login;