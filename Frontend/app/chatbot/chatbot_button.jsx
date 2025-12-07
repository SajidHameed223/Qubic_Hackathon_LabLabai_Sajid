"use client";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Bot } from "lucide-react";
export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const pathname = usePathname();
  const router = useRouter();

  // Exclude auth pages
  const excludedRoutes = ["/signin", "/signup", "/chatbot"];
  if (excludedRoutes.includes(pathname)) {
    return null;
  }

  const handleSend = () => {
    if (message.trim()) {
      router.push(`/chatbot?msg=${encodeURIComponent(message)}`);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-5 right-5 bg-blue-500 text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center text-2xl hover:bg-blue-700 transition"
      >
        <Bot />
      </button>

      {/* Chatbox */}
      {open && (
        <div className="fixed flex flex-col bottom-24 right-5 bg-white border border-gray-300 rounded-lg shadow-lg w-80 p-4">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSend}
              className="bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-700 transition flex items-center justify-center"
            >
              ⬆
            </button>
          </div>
        </div>
      )}
    </>
  );
}
