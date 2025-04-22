import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate, Outlet, Link } from "react-router-dom";
import { Building, User, LogOut } from "lucide-react";
import LandingPage from "./pages/LandingPage";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import SearchResultsPage from "./pages/SearchResultsPage";
import MapPage from "./pages/MapPage";
import SearchAndMapPage from "./pages/SearchAndMapPage";
import { useState, useEffect, useCallback } from "react";

// ProtectedRoute component (remains the same)
interface ProtectedRouteProps {
  children?: React.ReactNode;
}
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? <Outlet /> : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Authentication Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />

        {/* Main Application Routes */}
        <Route path="/*" element={<MainLayout />} />
      </Routes>
    </Router>
  );
}

// Main Layout Component
function MainLayout() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/", { replace: true });
  }, [navigate]);

  return (
    // Ensure the main layout allows content to take full height
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 h-16 flex-shrink-0"> {/* Fixed header height */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
          <div className="flex items-center justify-between h-full">
            {/* Logo and Brand Name */}
            <div className="flex items-center">
              <Building className="h-8 w-8 text-blue-600" />
              <Link to="/homepage" className="ml-2 text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                 LocaNova-IDF
              </Link>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center space-x-8">
              <nav className="hidden md:flex space-x-8">
                <Link to="/search-map" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Recherche et Carte
                </Link>
                {/* --- Changed back to React Router Link --- */}
                
              </nav>

              {/* User Icon and Logout */}
              {isLoggedIn && (
                 <div className="relative group">
                   <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors focus:outline-none">
                     <User className="w-6 h-6" />
                   </button>
                   <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-md shadow-lg opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto group-focus-within:pointer-events-auto z-10"> {/* Ensure dropdown is above map */}
                     <button
                       onClick={handleLogout}
                       className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                     >
                       <LogOut className="w-4 h-4 mr-2" />
                       Logout
                     </button>
                   </div>
                 </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Make it grow */}
      <main className="flex-1 overflow-y-auto"> {/* Allow content to scroll if needed */}
        <Routes>
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/homepage" element={<HomePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/search-map" element={<SearchAndMapPage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/results" element={<SearchResultsPage />} />
            {/* --- Added Analyse ML Route --- */}

            {/* Default route for logged-in users */}
            <Route index element={<Navigate to="/homepage" replace />} />
            {/* Catch-all for any other protected path */}
            <Route path="*" element={<Navigate to="/homepage" replace />} />
          </Route>
        </Routes>
      </main>

      {/* Footer - Make it shrink */}
      <footer className="bg-white border-t border-gray-200 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600">
            <p>Analyse des entreprises d'Île-de-France © 2025</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
