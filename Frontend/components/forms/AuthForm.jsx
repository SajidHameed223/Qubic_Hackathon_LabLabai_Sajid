"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function AuthForm({ mode = "signin", onSubmit }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [qubicID, setQubicID] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ name, email, qubicID, password });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-[#202020] p-8 rounded-xl shadow-md min-w-md mx-auto my-10 text-white"
    >
      <h2 className="text-2xl font-semibold mb-6 text-center">
        {mode === "signin" ? "Sign In" : "Sign Up"}
      </h2>

      {mode === "signup" && (
        <div className="mb-4">
          <label className="block text-sm mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-2 rounded bg-gray-800"
            required
          />
        </div>
      )}

      <div className="mb-4">
        <label className="block text-sm mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 rounded bg-gray-800"
          required
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm mb-1">Qubic ID</label>
        <input
          type="text"
          value={qubicID}
          onChange={(e) => setQubicID(e.target.value)}
          className="w-full p-2 rounded bg-gray-800"
          required
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 rounded bg-gray-800"
          required
        />
      </div>

      <button
        type="submit"
        className="w-full py-2 bg-blue-500 hover:bg-blue-700 rounded transition-colors cursor-pointer"
      >
        {mode === "signin" ? "Sign In" : "Sign Up"}
      </button>

      <div>
        <p className="font-semibold mt-3">Continue with</p>
      </div>

      {/* Toggle text + routes */}
      <div className="mt-4 text-sm text-gray-400 text-center">
        {mode === "signin" ? (
          <p>
            Don’t have an account?{" "}
            <Link href="/signup" className="text-blue-500 hover:underline">
              Sign Up
            </Link>
          </p>
        ) : (
          <p>
            Already have an account?{" "}
            <Link href="/signin" className="text-blue-500 hover:underline">
              Sign In
            </Link>
          </p>
        )}
      </div>
    </form>
  );
}