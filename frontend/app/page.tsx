"use client";

import { useEffect, useState } from "react";
import { VoiceRoom } from "./components/VoiceRoom";

interface AgentTemplate {
  name: string;
  description: string;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [roomName, setRoomName] = useState("test-room");
  const [participantName, setParticipantName] = useState("");
  const [isInRoom, setIsInRoom] = useState(false);
  const [enableAIAgent, setEnableAIAgent] = useState(true);
  const [selectedAgentType, setSelectedAgentType] = useState("study_partner");
  const [agentTemplates, setAgentTemplates] = useState<Record<string, AgentTemplate>>({});

  useEffect(() => {
    // Check backend health
    fetch("http://localhost:8000/health")
      .then((res) => res.json())
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Not connected"));
    
    // Fetch agent templates
    fetch("http://localhost:8000/api/agent-templates")
      .then((res) => res.json())
      .then((templates) => setAgentTemplates(templates))
      .catch((err) => console.error("Failed to fetch agent templates:", err));
  }, []);

  const handleJoinRoom = () => {
    if (participantName.trim()) {
      setIsInRoom(true);
    }
  };

  const handleLeaveRoom = () => {
    setIsInRoom(false);
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui", maxWidth: "800px", margin: "0 auto" }}>
      <h1>AiGroupchat</h1>
      <p>AI-powered group voice chat</p>
      <p style={{ color: "#666", marginTop: "1rem" }}>
        Backend status: <span style={{ fontWeight: "bold" }}>{backendStatus}</span>
      </p>

      {!isInRoom ? (
        <div style={{ marginTop: "2rem" }}>
          <h2>Join Voice Room</h2>
          <div style={{ marginTop: "1rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <label htmlFor="roomName" style={{ display: "block", marginBottom: "0.5rem" }}>
                Room Name:
              </label>
              <input
                id="roomName"
                type="text"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                style={{
                  padding: "0.5rem",
                  width: "100%",
                  maxWidth: "300px",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                }}
              />
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <label htmlFor="participantName" style={{ display: "block", marginBottom: "0.5rem" }}>
                Your Name:
              </label>
              <input
                id="participantName"
                type="text"
                value={participantName}
                onChange={(e) => setParticipantName(e.target.value)}
                placeholder="Enter your name"
                style={{
                  padding: "0.5rem",
                  width: "100%",
                  maxWidth: "300px",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                }}
              />
            </div>
            
            {/* Stage 5: Agent Selection */}
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", marginBottom: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={enableAIAgent}
                  onChange={(e) => setEnableAIAgent(e.target.checked)}
                  style={{ marginRight: "0.5rem" }}
                />
                Enable AI Agent
              </label>
            </div>
            
            {enableAIAgent && (
              <div style={{ marginBottom: "1rem" }}>
                <label htmlFor="agentType" style={{ display: "block", marginBottom: "0.5rem" }}>
                  Select AI Agent:
                </label>
                <select
                  id="agentType"
                  value={selectedAgentType}
                  onChange={(e) => setSelectedAgentType(e.target.value)}
                  style={{
                    padding: "0.5rem",
                    width: "100%",
                    maxWidth: "300px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                  }}
                >
                  {Object.entries(agentTemplates).map(([key, template]) => (
                    <option key={key} value={key}>
                      {template.name} - {template.description}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <button
              onClick={handleJoinRoom}
              disabled={!participantName.trim() || backendStatus !== "Connected"}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#0070f3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: participantName.trim() && backendStatus === "Connected" ? "pointer" : "not-allowed",
                opacity: participantName.trim() && backendStatus === "Connected" ? 1 : 0.5,
              }}
            >
              Join Room
            </button>
          </div>
        </div>
      ) : (
        <div style={{ marginTop: "2rem" }}>
          <h2>Voice Room: {roomName}</h2>
          <p>Connected as: {participantName}</p>
          <VoiceRoom
            roomName={roomName}
            participantName={participantName}
            enableAIAgent={enableAIAgent}
            agentType={selectedAgentType}
            onLeave={handleLeaveRoom}
          />
          <button
            onClick={handleLeaveRoom}
            style={{
              marginTop: "1rem",
              padding: "0.5rem 1rem",
              backgroundColor: "#dc3545",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Leave Room
          </button>
        </div>
      )}
    </main>
  );
}