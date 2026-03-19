import { useState } from "react";
import { PayPalButtons, PayPalScriptProvider } from "@paypal/react-paypal-js";
import BACKEND from "../config";
import "../css/PaymentModal.css";

const PAYPAL_CLIENT_ID = import.meta.env.VITE_PAYPAL_CLIENT_ID || "YOUR_PAYPAL_CLIENT_ID";

export default function PaymentModal({ onClose, onSuccess }) {
  const [tab, setTab] = useState("paypal");
  const [phone, setPhone] = useState("");
  const [card, setCard] = useState({ number: "", expiry: "", cvv: "", name: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const token = localStorage.getItem("token");
  const authHeader = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  // ── MTN MoMo ──────────────────────────────────────────────
  const handleMomo = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${BACKEND}/momo-pay`, {
        method: "POST",
        headers: authHeader,
        body: JSON.stringify({ phone }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "MoMo payment failed");
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Visa / Card ────────────────────────────────────────────
  const handleCard = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${BACKEND}/create-checkout-session`, {
        method: "POST",
        headers: authHeader,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Card payment failed");
      window.location.href = data.url;
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="pay-overlay" onClick={onClose}>
      <div className="pay-modal" onClick={(e) => e.stopPropagation()}>
        <button className="pay-close" onClick={onClose}>✕</button>
        <h2 className="pay-title">Choose Payment Method</h2>
        <p className="pay-amount">$4.99 / month</p>

        <div className="pay-tabs">
          {["paypal", "card", "momo"].map((t) => (
            <button
              key={t}
              className={`pay-tab ${tab === t ? "active" : ""}`}
              onClick={() => { setTab(t); setError(null); }}
            >
              {t === "paypal" && "💳 PayPal"}
              {t === "card" && "💳 Visa / Card"}
              {t === "momo" && "📱 MTN MoMo"}
            </button>
          ))}
        </div>

        {error && <p className="pay-error">{error}</p>}

        {/* ── PayPal ── */}
        {tab === "paypal" && (
          <div className="pay-section">
            <PayPalScriptProvider options={{ "client-id": PAYPAL_CLIENT_ID, currency: "USD" }}>
              <PayPalButtons
                style={{ layout: "vertical", color: "blue", shape: "rect" }}
                createOrder={(data, actions) =>
                  actions.order.create({
                    purchase_units: [{ amount: { value: "4.99" }, description: "Ridexa Premium" }],
                  })
                }
                onApprove={async (data, actions) => {
                  await actions.order.capture();
                  const res = await fetch(`${BACKEND}/paypal-confirm`, {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({ order_id: data.orderID }),
                  });
                  if (res.ok) onSuccess();
                  else setError("Payment captured but confirmation failed. Contact support.");
                }}
                onError={() => setError("PayPal encountered an error. Please try again.")}
              />
            </PayPalScriptProvider>
          </div>
        )}

        {/* ── Visa / Card via Stripe ── */}
        {tab === "card" && (
          <form className="pay-section" onSubmit={handleCard}>
            <input className="pay-input" placeholder="Cardholder Name" value={card.name}
              onChange={(e) => setCard({ ...card, name: e.target.value })} required />
            <input className="pay-input" placeholder="Card Number" maxLength={19} value={card.number}
              onChange={(e) => setCard({ ...card, number: e.target.value.replace(/\D/g, "").replace(/(.{4})/g, "$1 ").trim() })} required />
            <div className="pay-row">
              <input className="pay-input" placeholder="MM/YY" maxLength={5} value={card.expiry}
                onChange={(e) => {
                  let v = e.target.value.replace(/\D/g, "");
                  if (v.length >= 3) v = v.slice(0, 2) + "/" + v.slice(2);
                  setCard({ ...card, expiry: v });
                }} required />
              <input className="pay-input" placeholder="CVV" maxLength={4} value={card.cvv}
                onChange={(e) => setCard({ ...card, cvv: e.target.value.replace(/\D/g, "") })} required />
            </div>
            <button className="pay-btn card-btn" type="submit" disabled={loading}>
              {loading ? "Redirecting to Stripe..." : "Pay with Card"}
            </button>
          </form>
        )}

        {/* ── MTN MoMo ── */}
        {tab === "momo" && (
          <form className="pay-section" onSubmit={handleMomo}>
            <p className="pay-hint">Enter your MTN mobile number to receive a payment prompt.</p>
            <input
              className="pay-input"
              placeholder="e.g. 256771234567"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
              required
            />
            <button className="pay-btn momo-btn" type="submit" disabled={loading}>
              {loading ? "Sending prompt..." : "Pay with MTN MoMo"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
