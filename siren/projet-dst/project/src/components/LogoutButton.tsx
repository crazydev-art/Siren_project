import React from "react";

export default function LogoutButton() {
    const handleLogout = () => {
        localStorage.removeItem("token");  // ✅ Remove JWT token
        window.location.href = "/login";   // ✅ Redirect to login
    };

    return (
        <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded">
            Logout
        </button>
    );
}
