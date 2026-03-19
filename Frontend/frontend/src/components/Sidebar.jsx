import { useEffect, useState } from "react";
import "../css/Sidebar.css";
import MovieModal from "./MovieModal";

const API_KEY = "83709bf5d24c0f1ceba692299ef89107";
const BASE_URL = "https://api.themoviedb.org/3";

export default function Sidebar() {
  const [movies, setMovies] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const fetchTop100 = async () => {
      const pages = await Promise.all(
        [1, 2, 3, 4, 5].map((p) =>
          fetch(`${BASE_URL}/movie/top_rated?api_key=${API_KEY}&page=${p}`)
            .then((r) => r.json())
            .then((d) => d.results)
        )
      );
      setMovies(pages.flat().slice(0, 100));
    };
    fetchTop100();
  }, []);

  return (
    <>
    <aside className="sidebar">
      <h2 className="sidebar-title">IMDb Top 100</h2>
      <ol className="sidebar-list">
        {movies.map((movie, i) => (
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
    <MovieModal movie={selected} onClose={() => setSelected(null)} />
    </>
  );
}
