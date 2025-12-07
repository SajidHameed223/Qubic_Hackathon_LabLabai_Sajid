"use client";

import React, { useState } from "react";
import { Bell, User, ChevronDown, LogOut } from "lucide-react";
import { redirect } from "next/navigation";

const Navbar = ({ sidebarOpen }) => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const handleLogout =()=>{
    redirect("./signup")
  }
  return (
    <nav
      className={`h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6 transition-all duration-300 ${
        sidebarOpen ? "ml-64" : "ml-20"
      } fixed top-0 right-0 left-0 z-30`}
    >
      {/* Left: Page Title */}
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold text-white">Dashboard</h1>
        <span className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded">
          Production
        </span>
      </div>

      {/* Right: Icons & User */}
      <div className="flex items-center gap-4">
        {/* System Status */}
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          <span>Healthy</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 hover:bg-gray-800 rounded transition-colors">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-2 px-3 py-1.5 hover:bg-gray-800 rounded transition-colors"
          >
            <User size={18} />
            <span className="text-sm">Admin</span>
            <ChevronDown size={16} />
          </button>

          {/* Dropdown Menu */}
          {userMenuOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded shadow-lg z-50">
              <div className="px-4 py-2 border-b border-gray-700">
                <p className="text-sm font-medium text-white">John Admin</p>
                <p className="text-xs text-gray-400">admin@example.com</p>
              </div>
              <a
                href="#"
                className="block px-4 py-2 text-sm hover:bg-gray-700 transition-colors text-gray-200"
              >
                Profile
              </a>
              <a
                href="#"
                className="block px-4 py-2 text-sm hover:bg-gray-700 transition-colors text-gray-200"
              >
                Settings
              </a>
              <button className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 transition-colors text-red-400 border-t border-gray-700 mt-2 flex items-center gap-2" onClick={handleLogout}>
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
