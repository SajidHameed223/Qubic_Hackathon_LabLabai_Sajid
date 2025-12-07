"use client";

export default function GraphVisualizer({ agents, tasks }) {
  const roleColors = {
    Researcher: "bg-blue-300 border-blue-400",
    Analyst: "bg-green-300 border-green-400",
    Supervisor: "bg-purple-300 border-purple-400",
    Default: "bg-gray-300 border-gray-300",
  };

  return (
    <div className="p-4 border rounded">
      <h2 className="text-lg font-semibold">Agent Graph</h2>
      <ul className="space-y-2">
        {agents.map((a, idx) => (
          <li
            key={idx}
            className={`p-2 rounded border ${
              roleColors[a.role] || roleColors.Default
            }`}
          >
            <strong>{a.name}</strong> ({a.role}) → Tools: {a.tools.join(", ")}
          </li>
        ))}
      </ul>
      <h3 className="mt-4 font-semibold">Tasks</h3>
      <ul className="space-y-2">
        {tasks.map((t, idx) => (
          <li key={idx} className="p-2 bg-gray-700 rounded">
            {t.agent} is running: {t.task}
          </li>
        ))}
      </ul>
    </div>
  );
}