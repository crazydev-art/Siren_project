"use client"

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";  // ✅ Import API function
import { ArrowLeft } from "lucide-react";

export default function SignUpPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setLoading(true);
        setError("");
        setSuccess("");

        const result = await registerUser(username, email, password);

        if (result.success) {
            setSuccess("Account created! Redirecting to login...");
            setTimeout(() => navigate("/login"), 2000);
        } else {
            setError(result.message);
        }

        setLoading(false);
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
                    <button onClick={() => navigate("/")} className="flex items-center text-white/80 hover:text-white mb-6 transition-colors">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back
                    </button>

                    <h2 className="text-3xl font-bold text-white mb-6">Sign Up</h2>

                    {error && <p className="text-red-500 text-center">{error}</p>}
                    {success && <p className="text-green-500 text-center">{success}</p>}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required className="w-full p-3 bg-white/10 text-white" />
                        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full p-3 bg-white/10 text-white" />
                        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full p-3 bg-white/10 text-white" />
                        <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="w-full p-3 bg-white/10 text-white" />
                        <button type="submit" className="w-full bg-blue-600 text-white p-3 rounded">{loading ? "Creating Account..." : "Create Account"}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
