import React, {useEffect} from "react"; 
import { useNavigate } from "react-router-dom";

function ProtectedPage() {
    const navigate = useNavigate();

    useEffect(() => {
        const verifyToken = async () => {
            const token = localStorage.getItem('token');
            console.log(token)
        try {
            const response = await fetch(`http://localhost:8000/verify-token/${token}`);
            if (!response.ok) {
                throw new Error('Token verification failed');

            }
        } catch (error) {
            localStorage.removeItem('token');
            navigate('/login');
        }
    };

    verifyToken();
}, [navigate]);

return (
    <div>
        <h1>Protected Page</h1>
        <p>This page is only accessible to authenticated users.</p>
    </div>
);
}

export default ProtectedPage;