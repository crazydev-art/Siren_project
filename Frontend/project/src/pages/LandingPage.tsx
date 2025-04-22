"use client";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { Building } from "lucide-react"; // ✅ Import Building Icon

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <>
      {/* Navigation Bar */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Brand Logo with Building Icon */}
            <Link
              to="/"
              className="flex items-center space-x-2 cursor-pointer hover:text-blue-600 transition-colors"
            >
              <Building className="h-8 w-8 text-blue-600" /> {/* ✅ Added Icon */}
              <span className="text-2xl font-bold">LocaNova-IDF</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div
        className="h-screen w-full flex items-center justify-center relative"
        style={{
          backgroundImage:
            "url(https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Capture%20d%E2%80%99e%CC%81cran%202025-03-12%20a%CC%80%2021.07.40-Rawt4zQDQTxD81f4QWDeKbfKtGhYGP.png)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        {/* Subtle overlay for better visibility */}
        <div className="absolute inset-0 bg-blue-950/30"></div>

        {/* Authentication Buttons */}
        <div className="relative z-10 flex flex-col sm:flex-row gap-5 justify-center">
          <button
            onClick={() => navigate("/signup")}
            className="px-10 py-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl text-lg font-medium"
          >
            Sign Up
          </button>
          <button
            onClick={() => navigate("/login")}
            className="px-10 py-4 bg-white/10 backdrop-blur-sm text-white border border-white/30 rounded-full hover:bg-white/20 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl text-lg font-medium"
          >
            Sign In
          </button>
        </div>
      </div>
    </>
  );
}
