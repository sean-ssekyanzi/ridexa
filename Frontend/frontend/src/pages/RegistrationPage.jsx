import React, {useState} from 'react';
import axios from 'axios'

function RegistrationPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('https://app-image6-latest.onrender.com/register',{
                username,
                password,
            });
            setMessage(response.data.message);
            setError('');
        } catch (err) {
            setError(err.response.data.detail || 'An error occured');
            setMessage('');
        }
    };
    return (
        <div>
            <h2>Register</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>
                        Username:
                        <input type = "text" value={username} onChange={(e) => setUsername(e.target.value)} required />

                    </label>
                </div>
                <div>
                    <label>
                        Password:
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    </label>
                </div>
                <button type="submit">Register</button>
            </form>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            {error && <p style={{ color: 'red'}}>{error}</p>}
        </div>
    );
}

export default RegistrationPage