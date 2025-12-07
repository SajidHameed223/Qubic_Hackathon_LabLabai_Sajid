"use client";

export default function Home() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-1">Welcome to AutoPilot</h2>
        <p className="text-gray-400 text-sm">
          Monitor and manage your autonomous treasury rebalancing agents
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Active Agents", value: "12", change: "↑ 2" },
          { label: "Queue Depth", value: "45", change: "→ Stable" },
          { label: "Success Rate", value: "98.5%", change: "↑ 0.3%" },
          { label: "Error Rate", value: "1.5%", change: "↑ Improving" },
        ].map((metric, idx) => (
          <div
            key={idx}
            className="bg-gray-900 border border-gray-800 rounded p-4"
          >
            <p className="text-gray-400 text-sm mb-1">{metric.label}</p>
            <p className="text-3xl font-bold text-white">{metric.value}</p>
            <p className="text-xs text-green-400 mt-2">{metric.change}</p>
          </div>
        ))}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded p-4">
        <p className="text-gray-400">Content goes here...</p>
      </div>
    </div>
  );
}