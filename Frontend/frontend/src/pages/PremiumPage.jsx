import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/Premium.css";
import PaymentModal from "../components/PaymentModal";

export default function PremiumPage() {
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const handleSubscribe = () => {
    const token = localStorage.getItem("token");
    if (!token) { navigate("/login"); return; }
    setShowModal(true);
  };

  const handleSuccess = () => {
    setShowModal(false);
    navigate("/protected?premium=success");
  };

  return (
    <div className="premium-page">
      <div className="premium-card">
        <h1 className="premium-title">🎬 Go Ad-Free</h1>
        <p className="premium-subtitle">Enjoy uninterrupted streaming with no ads.</p>
        <ul className="premium-features">
          <li>✅ No ads on all movies</li>
          <li>✅ Full IMDb Top 100 access</li>
          <li>✅ Supports the platform</li>
        </ul>
        <div className="premium-price">$4.99 <span>/ month</span></div>
        <button className="premium-btn" onClick={handleSubscribe}>
          Subscribe Now
        </button>
      </div>

      {showModal && (
        <PaymentModal
          onClose={() => setShowModal(false)}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  );
}
