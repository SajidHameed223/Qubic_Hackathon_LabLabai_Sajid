"use client";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { User, Bot } from "lucide-react";

export default function AgentPage() {
  const searchParams = useSearchParams();
  const initialMsg = searchParams.get("msg") || "";
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Handle initial message from widget
  useEffect(() => {
    if (initialMsg) {
      const userMsg = { text: initialMsg, sender: "user" };
      const aiResponse = {
        text: "🤖 Mock AI response to: " + initialMsg,
        sender: "ai",
      };
      setMessages([userMsg, aiResponse]); // add both at once
    }
  }, [initialMsg]);

  const handleSend = () => {
    if (input.trim()) {
      const userMsg = { text: input, sender: "user" };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");

      setTimeout(() => {
        const aiResponse = {
          text: "🤖 Mock AI response to: " + input,
          sender: "ai",
        };
        setMessages((prev) => [...prev, aiResponse]);
      }, 600);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col min-h-screen">
        {/* Chat area */}
        <div className="flex-1 p-4 flex flex-col space-y-4">
          {messages.map((msg, idx) => {
            const isLast = idx === messages.length - 1;
            return (
              <div
                key={idx}
                className={`flex items-start ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                } ${msg.sender === "ai" && isLast ? "mb-16" : "mb-2"}`}
              >
                {/* Icon */}
                <div className="flex-shrink-0">
                  {msg.sender === "user" ? (
                    <div className="mx-2 w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  ) : (
                    <div className="mx-2 w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-black" />
                    </div>
                  )}
                </div>

                {/* Message bubble */}
                <div
                  className={`max-w-xs p-3 rounded-2xl ${
                    msg.sender === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-300 text-black"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            );
          })}
        </div>

        {/* Input area */}
        <div className="sticky bottom-0 w-full border-t bg-gray-100 p-4 flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border border-gray-400 text-black rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition flex items-center justify-center"
          >
            ⬆
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}