"use client"
import { useNavigate } from "react-router-dom"

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div
      className="min-h-screen w-full flex flex-col items-center justify-center relative"
      style={{
        backgroundImage:
          "url(https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Capture%20d%E2%80%99e%CC%81cran%202025-03-12%20a%CC%80%2021.07.40-Rawt4zQDQTxD81f4QWDeKbfKtGhYGP.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-950/30 to-blue-950/50"></div>

      {/* Content Container */}
      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        {/* Authentication Buttons */}
        <div className="flex flex-col sm:flex-row gap-5 justify-center mt-8">
          <button
            onClick={() => navigate("/search")}
            className="px-10 py-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl text-lg font-medium"
          >
            Enter 
          </button>
        </div>
      </div>
    </div>
  )
}

