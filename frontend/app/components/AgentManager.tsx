"use client";

import { useState, useEffect } from "react";
import styles from "../page.module.css";

interface Agent {
  id: string;
  name: string;
  instructions: string;
  voice_id: string;
  greeting: string;
  is_default: boolean;
  document_count: number;
}

interface Document {
  id: string;
  title: string;
  type: string;
  created_at: string;
  metadata?: {
    chunk_count?: number;
  };
}

interface AgentManagerProps {
  ownerName: string;
  onAgentsSelected: (agents: Agent[]) => void;
}

const VOICE_OPTIONS = [
  { id: "nPczCjzI2devNBz1zQrb", name: "Brian (Warm Male)" },
  { id: "EXAVITQu4vr4xnSDxMaL", name: "Sarah (Professional Female)" },
  { id: "TxGEqnHWrfWFTfGW9XjX", name: "Josh (Confident Male)" },
  { id: "pMsXgVXv3BLzUgSXRplE", name: "Serena (Friendly Female)" },
];

export function AgentManager({ ownerName, onAgentsSelected }: AgentManagerProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showKnowledge, setShowKnowledge] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [agentDocuments, setAgentDocuments] = useState<Record<string, Document[]>>({});
  const [newAgent, setNewAgent] = useState({
    name: "",
    instructions: "",
    voice_id: VOICE_OPTIONS[0].id,
    greeting: "",
  });

  useEffect(() => {
    if (ownerName) {
      loadAgents();
      loadDocuments();
    }
  }, [ownerName]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadAgents = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/agents?owner_id=${encodeURIComponent(ownerName)}`);
      if (response.ok) {
        const data = await response.json();
        setAgents(data);
        
        // Load linked documents for each custom agent
        const agentDocs: Record<string, Document[]> = {};
        for (const agent of data.filter((a: Agent) => !a.is_default)) {
          const docsResponse = await fetch(`http://localhost:8000/api/agents/${agent.id}/documents`);
          if (docsResponse.ok) {
            agentDocs[agent.id] = await docsResponse.json();
          }
        }
        setAgentDocuments(agentDocs);
      }
    } catch (error) {
      console.error("Failed to load agents:", error);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/documents?owner_id=${ownerName}`);
      if (response.ok) {
        const docs = await response.json();
        setDocuments(docs);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const createAgent = async () => {
    if (!newAgent.name || !newAgent.instructions || !newAgent.greeting) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/agents?owner_id=${encodeURIComponent(ownerName)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newAgent),
      });

      if (response.ok) {
        await loadAgents();
        setShowCreate(false);
        setNewAgent({
          name: "",
          instructions: "",
          voice_id: VOICE_OPTIONS[0].id,
          greeting: "",
        });
      }
    } catch (error) {
      console.error("Failed to create agent:", error);
    } finally {
      setLoading(false);
    }
  };

  const deleteAgent = async (agentId: string) => {
    if (!confirm("Delete this agent?")) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/agents/${agentId}?owner_id=${encodeURIComponent(ownerName)}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        await loadAgents();
        setSelectedAgents(selectedAgents.filter(a => a.id !== agentId));
      }
    } catch (error) {
      console.error("Failed to delete agent:", error);
    }
  };

  const toggleAgentSelection = (agent: Agent) => {
    const isSelected = selectedAgents.some(a => a.id === agent.id);
    if (isSelected) {
      setSelectedAgents(selectedAgents.filter(a => a.id !== agent.id));
    } else if (selectedAgents.length < 2) {
      setSelectedAgents([...selectedAgents, agent]);
    }
  };

  const toggleDocumentLink = async (agentId: string, documentId: string, isLinked: boolean) => {
    try {
      if (isLinked) {
        // Unlink document
        const response = await fetch(
          `http://localhost:8000/api/agents/${agentId}/documents/${documentId}`,
          { method: "DELETE" }
        );
        
        if (response.ok) {
          setAgentDocuments(prev => ({
            ...prev,
            [agentId]: prev[agentId]?.filter(doc => doc.id !== documentId) || []
          }));
          await loadAgents(); // Refresh document counts
        }
      } else {
        // Link document
        const response = await fetch(
          `http://localhost:8000/api/agents/${agentId}/documents`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ document_ids: [documentId] }),
          }
        );
        
        if (response.ok) {
          const document = documents.find(doc => doc.id === documentId);
          if (document) {
            setAgentDocuments(prev => ({
              ...prev,
              [agentId]: [...(prev[agentId] || []), document]
            }));
          }
          await loadAgents(); // Refresh document counts
        }
      }
    } catch (error) {
      console.error("Failed to toggle document link:", error);
    }
  };

  useEffect(() => {
    onAgentsSelected(selectedAgents);
  }, [selectedAgents, onAgentsSelected]);

  return (
    <div className={styles.agentManager}>
      <h3>AI Agents ({selectedAgents.length}/2 selected)</h3>
      
      <div className={styles.agentGrid}>
        {agents.map(agent => (
          <div
            key={agent.id}
            className={`${styles.agentCard} ${
              selectedAgents.some(a => a.id === agent.id) ? styles.selected : ""
            }`}
          >
            <div onClick={() => toggleAgentSelection(agent)}>
              <h4>{agent.name}</h4>
              <p className={styles.agentType}>{agent.is_default ? "Default" : "Custom"}</p>
              <p className={styles.agentDocs}>📚 {agent.document_count} documents</p>
            </div>
            
            {!agent.is_default && (
              <div className={styles.agentActions}>
                <button
                  className={styles.knowledgeBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowKnowledge(showKnowledge === agent.id ? null : agent.id);
                  }}
                >
                  Add Knowledge
                </button>
                <button
                  className={styles.deleteBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteAgent(agent.id);
                  }}
                >
                  Delete
                </button>
              </div>
            )}
            
            {/* Knowledge Management Panel */}
            {showKnowledge === agent.id && !agent.is_default && (
              <div className={styles.knowledgePanel}>
                <h5>Manage Knowledge for {agent.name}</h5>
                
                {/* Linked Documents */}
                {agentDocuments[agent.id]?.length > 0 && (
                  <div className={styles.linkedDocs}>
                    <h6>Linked Documents:</h6>
                    {agentDocuments[agent.id].map(doc => (
                      <div key={doc.id} className={styles.linkedDoc}>
                        <span>{doc.title}</span>
                        <button
                          onClick={() => toggleDocumentLink(agent.id, doc.id, true)}
                          className={styles.unlinkBtn}
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Available Documents */}
                <div className={styles.availableDocs}>
                  <h6>Available Documents:</h6>
                  {documents.length === 0 ? (
                    <p className={styles.noDocuments}>No documents uploaded yet</p>
                  ) : (
                    documents
                      .filter(doc => !agentDocuments[agent.id]?.some(linked => linked.id === doc.id))
                      .map(doc => (
                        <div key={doc.id} className={styles.availableDoc}>
                          <span>{doc.title}</span>
                          <button
                            onClick={() => toggleDocumentLink(agent.id, doc.id, false)}
                            className={styles.linkBtn}
                          >
                            Add
                          </button>
                        </div>
                      ))
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        
        <div
          className={styles.agentCard + " " + styles.createCard}
          onClick={() => setShowCreate(true)}
        >
          <div className={styles.createIcon}>+</div>
          <p>Create Agent</p>
        </div>
      </div>

      {showCreate && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h3>Create New Agent</h3>
            
            <input
              type="text"
              placeholder="Agent name"
              value={newAgent.name}
              onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              className={styles.input}
            />
            
            <textarea
              placeholder="Personality and instructions (e.g., 'You are a helpful math tutor who explains concepts clearly...')"
              value={newAgent.instructions}
              onChange={(e) => setNewAgent({ ...newAgent, instructions: e.target.value })}
              className={styles.textarea}
              rows={4}
            />
            
            <select
              value={newAgent.voice_id}
              onChange={(e) => setNewAgent({ ...newAgent, voice_id: e.target.value })}
              className={styles.select}
            >
              {VOICE_OPTIONS.map(voice => (
                <option key={voice.id} value={voice.id}>
                  {voice.name}
                </option>
              ))}
            </select>
            
            <input
              type="text"
              placeholder="Greeting message (e.g., 'Hello! I'm here to help with math.')"
              value={newAgent.greeting}
              onChange={(e) => setNewAgent({ ...newAgent, greeting: e.target.value })}
              className={styles.input}
            />
            
            <div className={styles.modalButtons}>
              <button onClick={() => setShowCreate(false)} disabled={loading}>
                Cancel
              </button>
              <button onClick={createAgent} disabled={loading}>
                {loading ? "Creating..." : "Create Agent"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}