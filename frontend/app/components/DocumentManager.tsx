"use client";

import { useState, useEffect } from "react";

interface Document {
  id: string;
  title: string;
  type: string;
  created_at: string;
  metadata?: {
    chunk_count?: number;
  };
}

interface DocumentManagerProps {
  participantName: string;
}

export function DocumentManager({ participantName }: DocumentManagerProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Fetch user's documents
  const fetchDocuments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/documents?owner_id=${participantName}`);
      if (response.ok) {
        const docs = await response.json();
        setDocuments(docs);
      }
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [participantName]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = [".pdf", ".txt", ".text"];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf("."));
    if (!validTypes.includes(fileExtension)) {
      setUploadError("Only PDF and TXT files are supported");
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);
    formData.append("owner_id", participantName);

    try {
      const response = await fetch("http://localhost:8000/api/documents", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadSuccess(`Document uploaded successfully! ${result.chunk_count} chunks created.`);
        fetchDocuments(); // Refresh document list
        // Clear file input
        event.target.value = "";
      } else {
        const error = await response.json();
        setUploadError(error.detail || "Failed to upload document");
      }
    } catch (error) {
      setUploadError("Network error: Failed to upload document");
      console.error("Upload error:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${documentId}?owner_id=${participantName}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        fetchDocuments(); // Refresh document list
      } else {
        console.error("Failed to delete document");
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  return (
    <div style={{ marginTop: "2rem", padding: "1rem", border: "1px solid #e0e0e0", borderRadius: "8px" }}>
      <h3>📚 Your Documents</h3>
      <p style={{ color: "#666", fontSize: "0.9rem", marginBottom: "1rem" }}>
        Upload documents to enhance AI agent responses with your content
      </p>

      {/* Upload Section */}
      <div style={{ marginBottom: "1.5rem" }}>
        <label
          htmlFor="file-upload"
          style={{
            display: "inline-block",
            padding: "0.5rem 1rem",
            backgroundColor: isUploading ? "#ccc" : "#28a745",
            color: "white",
            borderRadius: "4px",
            cursor: isUploading ? "not-allowed" : "pointer",
            fontSize: "0.9rem",
          }}
        >
          {isUploading ? "Uploading..." : "Upload Document"}
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".pdf,.txt,.text"
          onChange={handleFileUpload}
          disabled={isUploading}
          style={{ display: "none" }}
        />
        <span style={{ marginLeft: "1rem", color: "#666", fontSize: "0.85rem" }}>
          Supported: PDF, TXT
        </span>
      </div>

      {/* Status Messages */}
      {uploadError && (
        <div style={{ 
          padding: "0.5rem", 
          marginBottom: "1rem", 
          backgroundColor: "#f8d7da", 
          color: "#721c24", 
          borderRadius: "4px",
          fontSize: "0.9rem"
        }}>
          {uploadError}
        </div>
      )}
      
      {uploadSuccess && (
        <div style={{ 
          padding: "0.5rem", 
          marginBottom: "1rem", 
          backgroundColor: "#d4edda", 
          color: "#155724", 
          borderRadius: "4px",
          fontSize: "0.9rem"
        }}>
          {uploadSuccess}
        </div>
      )}

      {/* Document List */}
      <div>
        <h4 style={{ marginBottom: "0.5rem" }}>Uploaded Documents ({documents.length})</h4>
        {documents.length === 0 ? (
          <p style={{ color: "#666", fontSize: "0.9rem" }}>
            No documents uploaded yet. Upload PDFs or text files to provide context for AI agents.
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {documents.map((doc) => (
              <li
                key={doc.id}
                style={{
                  padding: "0.75rem",
                  marginBottom: "0.5rem",
                  backgroundColor: "#f8f9fa",
                  borderRadius: "4px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <strong>{doc.title}</strong>
                  <span style={{ marginLeft: "1rem", color: "#666", fontSize: "0.85rem" }}>
                    {doc.type.toUpperCase()}
                  </span>
                  {doc.metadata?.chunk_count && (
                    <span style={{ marginLeft: "0.5rem", color: "#666", fontSize: "0.85rem" }}>
                      ({doc.metadata.chunk_count} chunks)
                    </span>
                  )}
                  <div style={{ fontSize: "0.8rem", color: "#999", marginTop: "0.25rem" }}>
                    {new Date(doc.created_at).toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteDocument(doc.id)}
                  style={{
                    padding: "0.25rem 0.5rem",
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                  }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}