import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { PayPalButtons, PayPalScriptProvider } from '@paypal/react-paypal-js';
import BACKEND from '../config';
import '../css/Auth.css';

const PAYPAL_CLIENT_ID = import.meta.env.VITE_PAYPAL_CLIENT_ID || 'YOUR_PAYPAL_CLIENT_ID';

function RegistrationPage() {
    const [step, setStep] = useState(1);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [payTab, setPayTab] = useState('paypal');
    const [phone, setPhone] = useState('');
    const [card, setCard] = useState({ name: '', number: '', expiry: '', cvv: '' });
    const navigate = useNavigate();

    const getAuthHeader = () => ({
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
    });

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${BACKEND}/register`, { username, password });
            const tokenRes = await axios.post(
                `${BACKEND}/token`,
                new URLSearchParams({ username, password }),
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
            );
            localStorage.setItem('token', tokenRes.data.access_token);
            localStorage.setItem('username', username);
            window.dispatchEvent(new Event('login'));
            setError('');
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
            setStep(2);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleMomo = async (e) => {
        e.preventDefault();
        setLoading(true); setError('');
        try {
            const res = await fetch(`${BACKEND}/momo-pay`, {
                method: 'POST', headers: getAuthHeader(),
                body: JSON.stringify({ phone }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'MoMo payment failed');
            navigate('/protected');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCard = async (e) => {
        e.preventDefault();
        setLoading(true); setError('');
        try {
            const res = await fetch(`${BACKEND}/create-checkout-session`, {
                method: 'POST', headers: getAuthHeader(),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Card payment failed');
            window.location.href = data.url;
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card" style={{ maxWidth: step === 2 ? 460 : 400 }}>
                <div className="auth-logo">RIDEXA</div>
                {success && <p style={{ textAlign: 'center', color: '#4caf50', fontSize: '0.85rem', margin: '0.5rem 0' }}>✅ Account created successfully!</p>}

                {step === 1 ? (
                    <>
                        <p className="auth-subtitle">Create your account</p>
                        <form onSubmit={handleRegister}>
                            <div className="auth-field">
                                <label>Username</label>
                                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Choose a username" required />
                            </div>
                            <div className="auth-field">
                                <label>Password</label>
                                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Choose a password" required />
                            </div>
                            {error && <p className="auth-error">{error}</p>}
                            <button className="auth-btn" type="submit" disabled={loading}>
                                {loading ? 'Creating account...' : 'Continue'}
                            </button>
                        </form>
                        <p className="auth-footer">Already have an account? <Link to="/login">Sign in</Link></p>
                    </>
                ) : (
                    <>
                        <p className="auth-subtitle">Choose a payment plan — $4.99/month</p>

                        <div className="pay-tabs">
                            {['paypal', 'card', 'momo'].map((t) => (
                                <button key={t} className={`pay-tab ${payTab === t ? 'active' : ''}`}
                                    onClick={() => { setPayTab(t); setError(''); }}>
                                    {t === 'paypal' && '💳 PayPal'}
                                    {t === 'card' && '💳 Visa / Card'}
                                    {t === 'momo' && '📱 MTN MoMo'}
                                </button>
                            ))}
                        </div>

                        {error && <p className="auth-error">{error}</p>}

                        {payTab === 'paypal' && (
                            <div className="pay-section">
                                <PayPalScriptProvider options={{ 'client-id': PAYPAL_CLIENT_ID, currency: 'USD' }}>
                                    <PayPalButtons
                                        style={{ layout: 'vertical', color: 'blue', shape: 'rect' }}
                                        createOrder={(_, actions) =>
                                            actions.order.create({
                                                purchase_units: [{ amount: { value: '4.99' }, description: 'Ridexa Premium' }],
                                            })
                                        }
                                        onApprove={async (data, actions) => {
                                            await actions.order.capture();
                                            const res = await fetch(`${BACKEND}/paypal-confirm`, {
                                                method: 'POST', headers: getAuthHeader(),
                                                body: JSON.stringify({ order_id: data.orderID }),
                                            });
                                            if (res.ok) navigate('/protected');
                                            else setError('Payment captured but confirmation failed.');
                                        }}
                                        onError={() => setError('PayPal encountered an error.')}
                                    />
                                </PayPalScriptProvider>
                            </div>
                        )}

                        {payTab === 'card' && (
                            <form className="pay-section" onSubmit={handleCard}>
                                <input className="pay-input" placeholder="Cardholder Name" value={card.name}
                                    onChange={(e) => setCard({ ...card, name: e.target.value })} required />
                                <input className="pay-input" placeholder="Card Number" maxLength={19} value={card.number}
                                    onChange={(e) => setCard({ ...card, number: e.target.value.replace(/\D/g, '').replace(/(.{4})/g, '$1 ').trim() })} required />
                                <div className="pay-row">
                                    <input className="pay-input" placeholder="MM/YY" maxLength={5} value={card.expiry}
                                        onChange={(e) => {
                                            let v = e.target.value.replace(/\D/g, '');
                                            if (v.length >= 3) v = v.slice(0, 2) + '/' + v.slice(2);
                                            setCard({ ...card, expiry: v });
                                        }} required />
                                    <input className="pay-input" placeholder="CVV" maxLength={4} value={card.cvv}
                                        onChange={(e) => setCard({ ...card, cvv: e.target.value.replace(/\D/g, '') })} required />
                                </div>
                                <button className="pay-btn card-btn" type="submit" disabled={loading}>
                                    {loading ? 'Redirecting to Stripe...' : 'Pay with Card'}
                                </button>
                            </form>
                        )}

                        {payTab === 'momo' && (
                            <form className="pay-section" onSubmit={handleMomo}>
                                <p className="pay-hint">Enter your MTN mobile number to receive a payment prompt.</p>
                                <input className="pay-input" placeholder="e.g. 256771234567" value={phone}
                                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))} required />
                                <button className="pay-btn momo-btn" type="submit" disabled={loading}>
                                    {loading ? 'Sending prompt...' : 'Pay with MTN MoMo'}
                                </button>
                            </form>
                        )}

                        <button className="auth-btn" style={{ marginTop: '1rem', background: 'transparent', border: '1px solid #2a2a4a', color: '#888' }}
                            onClick={() => navigate('/login')}>
                            Skip for now
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}

export default RegistrationPage;