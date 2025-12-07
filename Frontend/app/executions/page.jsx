"use client";
import { useState } from "react";
import AgentForm from "./AgentForm";
import TaskRunner from "./TaskRunner";
import GraphVisualizer from "./GraphVisualizer";
import DashboardLayout from "@/components/layout/DashboardLayout";

export default function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);

  const handleCreateAgent = (agent) => {
    setAgents((prev) => [...prev, agent]);
  };

  const handleRunTask = (task) => {
    setTasks((prev) => [...prev, task]);
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6 p-6">
        <h1 className="text-2xl font-bold">Multi-Agent Dashboard</h1>
        <AgentForm onCreateAgent={handleCreateAgent} />
        <TaskRunner agents={agents} onRunTask={handleRunTask} />
        <GraphVisualizer agents={agents} tasks={tasks} />
      </div>
    </DashboardLayout>
  );
}
