import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../css/Premium.css";
import PaymentModal from "../components/PaymentModal";

const API_KEY = "83709bf5d24c0f1ceba692299ef89107";

export default function PremiumPage() {
  const [showModal, setShowModal] = useState(false);
  const [posters, setPosters] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`https://api.themoviedb.org/3/movie/top_rated?api_key=${API_KEY}&page=1`)
      .then((r) => r.json())
      .then((d) => setPosters(d.results?.slice(0, 20) || []));
  }, []);

  const handleSubscribe = () => {
    const token = localStorage.getItem("token");
    if (!token) { navigate("/login"); return; }
    setShowModal(true);
  };

  return (
    <div className="premium-layout">
      {/* Movie poster sidebar */}
      <div className="premium-sidebar">
        <div className="premium-poster-grid">
          {posters.map((m) => (
            <img
              key={m.id}
              src={`https://image.tmdb.org/t/p/w185${m.poster_path}`}
              alt={m.title}
              className="premium-poster-img"
            />
          ))}
        </div>
        <div className="premium-sidebar-overlay" />
      </div>

      {/* Premium card */}
      <div className="premium-panel">
        <div className="auth-card">
          <div className="auth-logo">RIDEXA</div>
          <p className="auth-subtitle">Unlock the full experience</p>

          <ul className="premium-features">
            <li><span className="pf-icon">🎬</span> Ad-free streaming on all titles</li>
            <li><span className="pf-icon">🏆</span> IMDb Top 100 sidebar</li>
            <li><span className="pf-icon">📺</span> 1080p quality selector</li>
            <li><span className="pf-icon">❤️</span> Unlimited favourites</li>
            <li><span className="pf-icon">⚡</span> Priority access to new releases</li>
          </ul>

          <div className="premium-price">
            $4.99 <span>/ month</span>
          </div>

          <button className="auth-btn" onClick={handleSubscribe}>
            Subscribe Now 👑
          </button>

          <p className="auth-footer">
            Already subscribed? <span className="auth-link" onClick={() => navigate("/protected")}>Go to My Movies</span>
          </p>
        </div>
      </div>

      {showModal && (
        <PaymentModal
          onClose={() => setShowModal(false)}
          onSuccess={() => { setShowModal(false); navigate("/protected"); }}
        />
      )}
    </div>
  );
}
