import { useEffect, useState, useRef } from "react";
import "../css/MovieModal.css";
import { usePremium } from "../hooks/usePremium";

const API_KEY = "83709bf5d24c0f1ceba692299ef89107";
const BASE_URL = "https://api.themoviedb.org/3";

export default function MovieModal({ movie, onClose }) {
  const [trailerId, setTrailerId] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [embedError, setEmbedError] = useState(false);
  const [quality, setQuality] = useState("720");
  const [fullscreen, setFullscreen] = useState(false);
  const [timestamp, setTimestamp] = useState(0);
  const [iframeKey, setIframeKey] = useState(0);
  const iframeRef = useRef(null);
  const qualitySwitch = useRef(false);
  const isPremium = usePremium();

  const qualityDims = { "480": { w: 854, h: 480 }, "720": { w: 1280, h: 720 }, "1080": { w: 1920, h: 1080 } };

  const toggleFullscreen = () => {
    const el = document.querySelector(".modal-player iframe");
    if (!el) return;
    if (!document.fullscreenElement) {
      el.requestFullscreen();
      setFullscreen(true);
    } else {
      document.exitFullscreen();
      setFullscreen(false);
    }
  };

  const handleQuality = (q) => {
    const iframe = iframeRef.current;
    if (iframe) {
      try { iframe.contentWindow.postMessage({ action: "getTime" }, "*"); } catch (_) {}
    }
    qualitySwitch.current = true;
    setQuality(q);
    setIframeKey((k) => k + 1);
  };

  // listen for time response from vidsrc
  useEffect(() => {
    const onMessage = (e) => {
      if (e.data?.currentTime !== undefined) {
        setTimestamp(Math.floor(e.data.currentTime));
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  // auto-engage playback after quality switch
  useEffect(() => {
    if (!playing || !qualitySwitch.current) return;
    qualitySwitch.current = false;
    const timer = setTimeout(() => {
      const iframe = iframeRef.current;
      if (!iframe) return;
      try { iframe.contentWindow.postMessage({ action: "play" }, "*"); } catch (_) {}
      iframe.focus();
      iframe.click();
    }, 800);
    return () => clearTimeout(timer);
  }, [iframeKey]);

  useEffect(() => {
    if (!movie) return;
    setPlaying(false);
    setEmbedError(false);
    setTimestamp(0);
    fetch(`${BASE_URL}/movie/${movie.id}/videos?api_key=${API_KEY}`)
      .then((r) => r.json())
      .then((d) => {
        const trailer = d.results?.find((v) => v.type === "Trailer" && v.site === "YouTube");
        setTrailerId(trailer?.key || null);
      });
  }, [movie]);

  if (!movie) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-header">
          <img
            className="modal-poster"
            src={`https://image.tmdb.org/t/p/w185${movie.poster_path}`}
            alt={movie.title}
          />
          <div>
            <h2 className="modal-title">{movie.title}</h2>
            <p className="modal-meta">⭐ {movie.vote_average.toFixed(1)} · {movie.release_date?.slice(0, 4)}</p>
            <p className="modal-overview">{movie.overview}</p>
          </div>
        </div>

        <div className={`modal-player${fullscreen ? " modal-player--fs" : ""}`}
          style={playing && !fullscreen ? { aspectRatio: `${qualityDims[quality].w}/${qualityDims[quality].h}` } : {}}
        >
          {playing ? (
            embedError ? (
              <div className="embed-error">
                ⚠️ Stream unavailable for this title.
                <button onClick={() => { setPlaying(false); setEmbedError(false); }}>Go back</button>
              </div>
            ) : (
              <>
                <iframe
                  ref={iframeRef}
                  key={iframeKey}
                  src={`https://vidsrc.icu/embed/movie/${movie.id}${timestamp ? `#t=${timestamp}` : ""}`}
                  title={movie.title}
                  width={qualityDims[quality].w}
                  height={qualityDims[quality].h}
                  allowFullScreen
                  allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                  referrerPolicy="no-referrer"
                  onError={() => setEmbedError(true)}
                />
                <div className="player-controls">
                  <div className="quality-btns">
                    {["480", "720", "1080"].map((q) => (
                      <button key={q} className={`quality-btn ${quality === q ? "active" : ""}`} onClick={() => handleQuality(q)}>{q}p</button>
                    ))}
                  </div>
                  <button className="fs-btn" onClick={toggleFullscreen}>⛶ Fullscreen</button>
                </div>
              </>
            )
          ) : (
            <div className="player-placeholder" style={{
              backgroundImage: `url(https://image.tmdb.org/t/p/w780${movie.backdrop_path})`
            }}>
              <button className="play-btn" onClick={() => setPlaying(true)}>▶ Watch Now</button>
              {trailerId && (
                <a
                  className="trailer-btn"
                  href={`https://www.youtube.com/watch?v=${trailerId}`}
                  target="_blank"
                  rel="noreferrer"
                >🎬 Trailer</a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
