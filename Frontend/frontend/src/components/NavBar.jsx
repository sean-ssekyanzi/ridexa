import { Link, useNavigate } from "react-router-dom";
import "../css/Navbar.css"
import React, { useState, useEffect, useRef } from "react";
import BACKEND from "../config";

function NavBar() {
    const [username, setUsername] = useState(null);
    const [isPremium, setIsPremium] = useState(false);
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const stored = localStorage.getItem('username');
        if (stored) setUsername(stored);
        const onLogin = () => {
            const u = localStorage.getItem('username');
            setUsername(u);
            fetchPremium();
        };
        window.addEventListener('login', onLogin);
        return () => window.removeEventListener('login', onLogin);
    }, []);

    useEffect(() => { if (username) fetchPremium(); }, [username]);

    const fetchPremium = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            const res = await fetch(`${BACKEND}/me`, { headers: { Authorization: `Bearer ${token}` } });
            const data = await res.json();
            setIsPremium(data.is_premium ?? false);
        } catch {}
    };

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target))
                setOpen(false);
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        setUsername(null);
        setIsPremium(false);
        setOpen(false);
        navigate('/');
    };

    return <nav className="navbar">
        <div className="navbar-brand">
            <Link to="/">Movie App</Link>
        </div>
        <div className="navbar-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/favorites" className="nav-link">Favorites</Link>
            {!username && <Link to="/login" className="nav-link">Login</Link>}
            {!username && <Link to="/register" className="nav-link">Register</Link>}
            {username && (
                <div className="user-menu" ref={dropdownRef}>
                    <button className="avatar-btn" onClick={() => setOpen((o) => !o)}>
                        {username[0].toUpperCase()}
                    </button>
                    {open && (
                        <div className="user-dropdown">
                            <span className="dropdown-name">{username}{isPremium && <span className="premium-badge"> 👑</span>}</span>
                            {isPremium
                                ? <button onClick={() => { navigate('/protected'); setOpen(false); }} className="dropdown-item">🎬 My Movies</button>
                                : <button onClick={() => { navigate('/premium'); setOpen(false); }} className="dropdown-item premium">👑 Go Premium</button>
                            }
                            <button onClick={handleLogout} className="dropdown-item logout">⏻ Logout</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    </nav>
}

export default NavBar