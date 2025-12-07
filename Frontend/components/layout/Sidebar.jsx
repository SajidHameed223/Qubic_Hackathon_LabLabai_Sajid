"use client";

import React from "react";
import Link from "next/link";
import { redirect, usePathname } from "next/navigation";
import {
  Menu,
  X,
  Home,
  CheckSquare,
  Wallet,
  Play,
  FileText,
  BarChart3,
  Bot ,
  Settings,
  LogOut,
} from "lucide-react";

const Sidebar = ({ isOpen, setIsOpen }) => {
  const pathname = usePathname();

  const navItems = [
    { icon: Home, label: "Dashboard", href: "/dashboard" },
    { icon: Wallet, label: "Wallet", href: "/wallet" },
    { icon: CheckSquare, label: "Tasks", href: "/tasks" },
    { icon: Play, label: "Executions", href: "/executions" },
    { icon: FileText, label: "Approvals", href: "/approvals" },
    { icon: Bot, label: "Chatbot", href: "/chatbot" },
    { icon: BarChart3, label: "Agent Health", href: "/agent-health" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ];

  const isActive = (href) => {
    if (!pathname) return false;
    if (href === "/" && pathname === "/") return true;
    if (href !== "/" && pathname.startsWith(href)) return true;
    return false;
  };

  const handleLogout = () => {
    console.log("Logging out...");
    redirect("/signup")
  };

  return (
    <aside
      className={`${
        isOpen ? "w-64" : "w-20"
      } bg-gray-900 border-r border-gray-800 transition-all duration-300 flex flex-col h-screen fixed left-0 top-0 z-40`}
    >
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800">
        {isOpen && (
          <Link
            href="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white text-sm">
              AP
            </div>
            <span className="font-semibold text-sm">AutoPilot</span>
          </Link>
        )}
        {!isOpen && (
          <Link href="/" className="flex items-center justify-center w-full">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white text-sm">
              AP
            </div>
          </Link>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 hover:bg-gray-800 rounded transition-colors ml-auto"
          aria-label="Toggle sidebar"
        >
          {isOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-2">
        {navItems.map((item, idx) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={idx}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded text-sm transition-colors duration-200 ${
                active
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              }`}
              title={!isOpen ? item.label : ""}
            >
              <Icon size={18} className="flex-shrink-0" />
              {isOpen && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer - Logout Button */}
      <div className="border-t border-gray-800 p-2">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-sm text-gray-400 hover:bg-gray-800 hover:text-gray-200 transition-colors duration-200"
          title={!isOpen ? "Logout" : ""}
        >
          <LogOut size={18} className="flex-shrink-0" />
          {isOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;