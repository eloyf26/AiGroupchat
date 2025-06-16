"use client";

import { useEffect, useState } from "react";
import { VoiceRoom } from "./components/VoiceRoom";
import { DocumentManager } from "./components/DocumentManager";
import { AgentManager } from "./components/AgentManager";

interface Agent {
  id: string;
  name: string;
  instructions: string;
  voice_id: string;
  greeting: string;
  is_default: boolean;
  document_count: number;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [roomName, setRoomName] = useState("test-room");
  const [participantName, setParticipantName] = useState("");
  const [isInRoom, setIsInRoom] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([]);

  useEffect(() => {
    // Check backend health
    fetch("http://localhost:8000/health")
      .then((res) => res.json())
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Not connected"));
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
            
            {/* Agent Selection */}
            {participantName.trim() && (
              <AgentManager 
                ownerName={participantName} 
                onAgentsSelected={setSelectedAgents}
              />
            )}
            
            <button
              onClick={handleJoinRoom}
              disabled={!participantName.trim() || backendStatus !== "Connected" || selectedAgents.length === 0}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#0070f3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: participantName.trim() && backendStatus === "Connected" && selectedAgents.length > 0 ? "pointer" : "not-allowed",
                opacity: participantName.trim() && backendStatus === "Connected" && selectedAgents.length > 0 ? 1 : 0.5,
              }}
            >
              Join Room
            </button>
          </div>
          
          {/* Document Manager - Show after name is entered */}
          {participantName.trim() && backendStatus === "Connected" && (
            <DocumentManager participantName={participantName} />
          )}
        </div>
      ) : (
        <div style={{ marginTop: "2rem" }}>
          <h2>Voice Room: {roomName}</h2>
          <p>Connected as: {participantName}</p>
          <VoiceRoom
            roomName={roomName}
            participantName={participantName}
            enableAIAgent={selectedAgents.length > 0}
            agentType={selectedAgents[0]?.id || ""}
            agentTypes={selectedAgents.map(a => a.id)}
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