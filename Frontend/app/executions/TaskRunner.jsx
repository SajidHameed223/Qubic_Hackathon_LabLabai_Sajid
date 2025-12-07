"use client";
import { useState } from "react";

export default function TaskRunner({ agents, onRunTask }) {
  const [task, setTask] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("");

  const handleRun = () => {
    if (!task || !selectedAgent) return;
    onRunTask({ agent: selectedAgent, task });
    setTask("");
  };

  return (
    <div className="space-y-4 p-4 border rounded">
      <h2 className="text-lg font-semibold">Run Task</h2>
      <select
        value={selectedAgent}
        onChange={(e) => setSelectedAgent(e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="" className="bg-gray-500">Select Agent</option>
        {agents.map((a, idx) => (
          <option className="bg-gray-500 " key={idx} value={a.name}>
            {a.name} ({a.role})
          </option>
        ))}
      </select>
      <input
        type="text"
        placeholder="Enter task description"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button
        onClick={handleRun}
        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
      >
        Run Task
      </button>
    </div>
  );
}