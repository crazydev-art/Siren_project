"use client"

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";  // ✅ Import API function
import { ArrowLeft } from "lucide-react";

export default function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
  
    const handleLogin = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError("");
  
      console.log("🔍 Attempting login...");
  
      try {
        const result = await loginUser(email, password);
        console.log("🔍 API Response:", result);
  
        if (result.success) {
          console.log("✅ Login successful! Redirecting...");
          // Store the JWT in localStorage
          localStorage.setItem("token", result.token); // Assuming your API returns { success: true, token: 'your_jwt' }
          navigate("/search");
        } else {
          setError(result.message);
        }
      } catch (error) {
        console.error("🚨 Login Error:", error);
        setError("Something went wrong. Please try again.");
      } finally {
        setLoading(false);
      }
    };
  
  

    return (
        <div
            className="min-h-screen w-full flex items-center justify-center relative py-12"
            style={{
                backgroundImage:
                    "url(https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Capture%20d%E2%80%99e%CC%81cran%202025-03-12%20a%CC%80%2021.07.40-Rawt4zQDQTxD81f4QWDeKbfKtGhYGP.png)",
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
            }}
        >
            {/* Overlay for better form visibility */}
            <div className="absolute inset-0 bg-blue-950/40"></div>

            {/* Form Container */}
            <div className="relative z-10 w-full max-w-md px-6">
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-xl border border-white/20">
                    {/* Back Button */}
                    <button
                        onClick={() => navigate("/")}
                        className="flex items-center text-white/80 hover:text-white mb-6 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back
                    </button>

                    <h2 className="text-3xl font-bold text-white mb-6">Login</h2>

                    {/* Show error message */}
                    {error && <p className="text-red-500 text-center">{error}</p>}

                    <form onSubmit={handleLogin} className="space-y-5">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-white mb-1">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="your@email.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-white mb-1">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium mt-2"
                            disabled={loading}
                        >
                            {loading ? "Logging in..." : "Login"}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-white/80">
                            Don't have an account?{" "}
                            <button onClick={() => navigate("/signup")} className="text-white hover:underline font-medium">
                                Sign Up
                            </button>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
