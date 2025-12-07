"use client";
import { getToken } from "@/lib/auth";
import { useState, useEffect } from "react";
import { useRequireAuth } from "../hooks/page";
                   

export default function DashboardPage() {
  // Redirects to /signin if no token
  useRequireAuth();

  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = getToken();
    if (token) {
      fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => {
          if (!res.ok) throw new Error("Unauthorized");
          return res.json();
        })
        .then((data) => setUser(data))
        .catch((err) => console.error("Failed to fetch user:", err));
    }
  }, []);

  if (!user) return <p className="text-white">Loading...</p>;

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl font-bold">Welcome, {user.full_name}!</h1>
      <p>Email: {user.email}</p>
      <p>Account created: {new Date(user.created_at).toLocaleString()}</p>
    </div>
  );
}