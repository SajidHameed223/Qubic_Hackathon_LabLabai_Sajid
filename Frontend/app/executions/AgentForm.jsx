"use client";
import { useState } from "react";

export default function AgentForm({ onCreateAgent }) {
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [tools, setTools] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreateAgent({ name, role, tools: tools.split(",") });
    setName("");
    setRole("");
    setTools("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded">
      <h2 className="text-lg font-semibold">Create Agent</h2>
      <input
        type="text"
        placeholder="Agent Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        placeholder="Role (e.g. Researcher)"
        value={role}
        onChange={(e) => setRole(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        placeholder="Tools (comma separated)"
        value={tools}
        onChange={(e) => setTools(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Add Agent
      </button>
    </form>
  );
}