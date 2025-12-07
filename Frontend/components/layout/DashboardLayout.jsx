"use client"
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import { useState } from "react";

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="bg-[#101010] min-h-screen text-gray-100">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* Content Wrapper that shifts based on sidebar state */}
      <div
        className={`transition-all duration-300 flex flex-col ${
          sidebarOpen ? "ml-64" : "ml-20"
        }`}
      >
        {/* Navbar */}
        <Navbar sidebarOpen={sidebarOpen} />

        {/* Main */}
        <main className="mt-16 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
