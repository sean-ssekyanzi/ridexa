import "./css/App.css";
import Favorites from "./pages/Favorites";
import Home from "./pages/Home";
import Login from "./pages/Login";
import ProtectedPage from "./pages/Protected";
import PremiumPage from "./pages/PremiumPage";
import { Routes, Route } from "react-router-dom";
import { MovieProvider } from "./contexts/MovieContext";
import NavBar from "./components/NavBar";
import RegistrationPage from "./pages/RegistrationPage";

function App() {
  return (
    <MovieProvider>
      <NavBar />
      <div className="app-body">
        <main className="main-content">
          <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/protected" element={<ProtectedPage />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/register" element={<RegistrationPage />} />
          <Route path="/premium" element={<PremiumPage />} />
          </Routes>
        </main>
      </div>
    </MovieProvider>
  );
}

export default App;