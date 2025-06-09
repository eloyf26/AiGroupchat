"use client";

import { useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  ParticipantTile,
  useTracks,
  useParticipants,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { Track } from "livekit-client";

interface VoiceRoomProps {
  roomName: string;
  participantName: string;
  enableAIAgent?: boolean;
  agentType?: string;
  onLeave: () => void;
}

export function VoiceRoom({ roomName, participantName, enableAIAgent = true, agentType = "study_partner", onLeave }: VoiceRoomProps) {
  const [token, setToken] = useState<string>("");
  const [serverUrl, setServerUrl] = useState<string>("");
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string>("");

  const connectToRoom = async () => {
    setIsConnecting(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          room_name: roomName,
          participant_name: participantName,
          enable_ai_agent: enableAIAgent,
          agent_type: agentType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get token");
      }

      const data = await response.json();
      setToken(data.token);
      setServerUrl(data.url);
    } catch (err) {
      setError("Failed to connect to room");
      setIsConnecting(false);
    }
  };

  if (!token) {
    return (
      <div style={{ padding: "2rem" }}>
        <button
          onClick={connectToRoom}
          disabled={isConnecting}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: isConnecting ? "not-allowed" : "pointer",
            opacity: isConnecting ? 0.7 : 1,
          }}
        >
          {isConnecting ? "Connecting..." : "Join Voice Room"}
        </button>
        {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={onLeave}
      style={{ height: "400px" }}
    >
      <RoomContent />
      <RoomAudioRenderer />
      <ControlBar
        controls={{
          microphone: true,
          chat: false,
          camera: false,
          screenShare: false,
        }}
      />
    </LiveKitRoom>
  );
}

function RoomContent() {
  const participants = useParticipants();

  return (
    <div style={{ padding: "1rem" }}>
      <h3>Participants:</h3>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "1rem",
          marginTop: "1rem",
        }}
      >
        {participants.map((participant) => {
          const isAgent = participant.identity.startsWith("AI_");
          return (
            <div
              key={participant.identity}
              style={{
                padding: "1rem",
                border: "1px solid #ccc",
                borderRadius: "8px",
                backgroundColor: isAgent ? "#f0f8ff" : "#fff",
              }}
            >
              <div style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
                {isAgent ? "🤖 " : "👤 "}
                {participant.identity.replace("AI_", "")}
              </div>
              <div style={{ fontSize: "0.875rem", color: "#666" }}>
                {isAgent ? "AI Assistant" : "Human Participant"}
              </div>
              <div style={{ fontSize: "0.75rem", marginTop: "0.5rem" }}>
                {participant.isSpeaking ? "🔊 Speaking" : "🔇 Silent"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}