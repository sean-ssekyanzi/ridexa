import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MovieCard from "../components/MovieCard";
import MovieModal from "../components/MovieModal";
import { searchMovies, getPopularMovies } from "../servcs/mapi";
import BACKEND from "../config";
import "../css/Protected.css";
import "../css/Sidebar.css";

const API_KEY = "83709bf5d24c0f1ceba692299ef89107";
const BASE_URL = "https://api.themoviedb.org/3";

function PremiumMovies() {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState("");
    const [movies, setMovies] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [top100, setTop100] = useState([]);
    const [selected, setSelected] = useState(null);

    useEffect(() => {
        const verify = async () => {
            const token = localStorage.getItem("token");
            if (!token) { navigate("/login"); return; }
            try {
                const res = await fetch(`${BACKEND}/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.status === 401) {
                    localStorage.removeItem("token");
                    localStorage.removeItem("username");
                    navigate("/login");
                    return;
                }
                if (res.ok) {
                    const data = await res.json();
                    if (!data.is_premium) navigate("/premium");
                }
            } catch {}
        };
        verify();
    }, [navigate]);

    useEffect(() => {
        Promise.all(
            [1, 2, 3, 4, 5].map((p) =>
                fetch(`${BASE_URL}/movie/top_rated?api_key=${API_KEY}&page=${p}`)
                    .then((r) => r.json())
                    .then((d) => d.results)
            )
        ).then((pages) => setTop100(pages.flat().slice(0, 100)));
    }, []);

    useEffect(() => {
        getPopularMovies()
            .then(setMovies)
            .catch(() => setError("Failed to load movies..."))
            .finally(() => setLoading(false));
    }, []);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim() || loading) return;
        setLoading(true);
        try {
            setMovies(await searchMovies(searchQuery));
            setError(null);
        } catch {
            setError("Failed to search movies...");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div style={{ color: "white", textAlign: "center", padding: "2rem" }}>Loading...</div>;

    return (
        <div className="protected-layout">
            <aside className="sidebar">
                <h2 className="sidebar-title">IMDb Top 100</h2>
                <ol className="sidebar-list">
                    {top100.map((movie, i) => (
                        <li key={movie.id} className="sidebar-item" onClick={() => setSelected(movie)}>
                            <span className="sidebar-rank">{i + 1}</span>
                            <img
                                className="sidebar-poster"
                                src={`https://image.tmdb.org/t/p/w92${movie.poster_path}`}
                                alt={movie.title}
                            />
                            <div className="sidebar-info">
                                <span className="sidebar-name">{movie.title}</span>
                                <span className="sidebar-rating">⭐ {movie.vote_average.toFixed(1)}</span>
                            </div>
                        </li>
                    ))}
                </ol>
            </aside>

            <div className="protected-main">
                <form onSubmit={handleSearch} className="search-form">
                    <input
                        type="text"
                        placeholder="Search for movies..."
                        className="search-input"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <button type="submit" className="search-button">Search</button>
                </form>

                {error && <div style={{ color: "red", textAlign: "center", margin: "1rem 0" }}>{error}</div>}

                <div className="protected-grid">
                    {movies.map((movie) => (
                        <MovieCard movie={movie} key={movie.id} />
                    ))}
                </div>
            </div>

            <MovieModal movie={selected} onClose={() => setSelected(null)} />
        </div>
    );
}

export default PremiumMovies;
