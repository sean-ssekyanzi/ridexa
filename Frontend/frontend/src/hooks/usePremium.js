import { useEffect, useState } from "react";
import BACKEND from "../config";

export function usePremium() {
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch(`${BACKEND}/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => setIsPremium(d.is_premium ?? false))
      .catch(() => {});
  }, []);

  return isPremium;
}
