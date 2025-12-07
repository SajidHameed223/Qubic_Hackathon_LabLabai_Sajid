"use client";

import React from "react";
import { Globe, CreditCard } from "lucide-react";

export default function OAuthButtons({ onGoogle, onQubic }) {
  return (
    <div className="flex flex-row gap-4 max-w-md mx-auto mt-4">
      {/* Google Button */}
      <button
        onClick={onGoogle}
        className="flex items-center justify-center gap-2 flex-1 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors"
      >
        <Globe size={18} />
        <span>Google</span>
      </button>

      {/* Qubic Button */}
      <button
        onClick={onQubic}
        className="flex items-center justify-center gap-2 flex-1 py-2 bg-purple-600 hover:bg-purple-700 rounded transition-colors"
      >
        <CreditCard size={18} />
        <span>Qubic</span>
      </button>
    </div>
  );
}