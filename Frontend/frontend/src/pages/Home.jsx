import MovieCard from "../components/MovieCard"

function Home() {
    const movies = [
        {title: "The Shawshank Redemption", release_date: "1994-09-23", url: "https://m.media-amazon.com/images/I/51NiGlapXlL._AC_.jpg"},
        {title: "The Godfather", release_date: "1972-03-24", url: "https://m.media-amazon.com/images/I/41+eK8zBwQL._AC_.jpg"},
        {title: "The Dark Knight", release_date: "2008-07-18", url: "https://m.media-amazon.com/images/I/51EbJjlLJLL._AC_.jpg"},
    ]

    const handleSearch = () => {

    }
    return (
    <div className="home">
        <form onSubmit={handleSearch} className="search-form">
            <input type="text" placeholder="search for movies..." className="search-input"/>
            <button/>
        </form>
        <div className="movies-grid">
        {movies.map(movie => <MovieCard movie={movie} key={movie.id}/>)}
        </div>
    </div>
    );
}

export default Home