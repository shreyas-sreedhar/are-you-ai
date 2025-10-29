"use client";

import { useState, useEffect } from "react";

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    videos_protected: 0,
    scams_detected: 0,
    messages_analyzed: 0,
    active_alerts: 0,
  });
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Fetch metrics
      const metricsRes = await fetch("http://localhost:8000/api/v1/dashboard/metrics");
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);

      // Fetch alerts
      const alertsRes = await fetch("http://localhost:8000/api/v1/dashboard/alerts?limit=20");
      const alertsData = await alertsRes.json();
      setAlerts(alertsData);

      setLoading(false);
    } catch (error) {
      console.error("Error loading data:", error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ color: "white", fontSize: "24px" }}>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", padding: "24px" }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        {/* Header */}
        <header style={{ background: "white", borderRadius: "16px", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", padding: "24px", marginBottom: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h1 style={{ fontSize: "32px", fontWeight: "bold", color: "#333", margin: 0 }}>
                TrustGuard AI Dashboard - Building using Nvidia 
              </h1>
              <p style={{ color: "#666", marginTop: "8px" }}>
                Real-time content verification and scam protection
              </p>
            </div>
            <button
              onClick={loadData}
              style={{
                padding: "10px 20px",
                background: "#667eea",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              🔄 Refresh
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "20px", marginBottom: "24px" }}>
          <StatCard icon="✅" value={metrics.videos_protected} label="Content Verified" color="#4caf50" />
          <StatCard icon="🚨" value={metrics.scams_detected} label="Threats Detected" color="#f44336" />
          <StatCard icon="💬" value={metrics.messages_analyzed} label="Messages Scanned" color="#2196f3" />
          <StatCard icon="⚠️" value={metrics.active_alerts} label="Active Alerts" color="#ff9800" />
        </div>

        {/* Protection Status */}
        <div style={{ background: "white", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.08)", padding: "24px", marginBottom: "24px" }}>
          <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#333", marginBottom: "16px" }}>
            Protection Status
          </h2>
          <div
            style={{
              background: "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)",
              borderRadius: "12px",
              padding: "20px",
              borderLeft: "4px solid #4caf50",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: "#4caf50",
                  animation: "pulse 2s infinite",
                }}
              ></div>
              <span style={{ fontSize: "18px", fontWeight: "bold", color: "#2e7d32" }}>Active Protection</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
              <StatusItem label="Video Protection:" value="Enabled" />
              <StatusItem label="Message Monitoring:" value="Enabled" />
              <StatusItem label="AI Analysis:" value="Connected" />
              <StatusItem label="Last Scan:" value="Just now" />
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        <div style={{ background: "white", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.08)", padding: "24px", marginBottom: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#333" }}>Recent Alerts</h2>
          </div>

          {alerts.length === 0 ? (
            <div style={{ textAlign: "center", padding: "60px 20px" }}>
              <div style={{ fontSize: "64px", marginBottom: "16px" }}>✨</div>
              <div style={{ color: "#999", fontSize: "16px" }}>No alerts yet - you're protected!</div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {alerts.map((alert: any) => (
                <AlertCard key={alert.id} alert={alert} />
              ))}
            </div>
          )}
        </div>

        {/* Multi-Agent System
        <div style={{ background: "white", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.08)", padding: "24px", marginBottom: "24px" }}>
          <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#333", marginBottom: "16px" }}>
            🤖 Multi-Agent AI System
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "16px" }}>
            <AgentCard
              icon="👁️"
              name="Vision Agent"
              model="12B Vision-Language Model"
              description="Analyzes video frames"
              color="#2196f3"
            />
            <AgentCard
              icon="⏱️"
              name="Temporal Agent"
              model="9B Reasoning Model"
              description="Checks frame consistency"
              color="#9c27b0"
            />
            <AgentCard
              icon="🔍"
              name="Research Agent"
              model="9B Reasoning Model"
              description="Searches patterns"
              color="#4caf50"
            />
            <AgentCard
              icon="✅"
              name="Fact-Checker"
              model="9B Reasoning Model"
              description="Verifies claims"
              color="#ff9800"
            />
            <AgentCard
              icon="🛡️"
              name="Safety Guard"
              model="8B Safety Model"
              description="Checks harm"
              color="#f44336"
            />
            <AgentCard
              icon="🎯"
              name="Orchestrator"
              model="49B Advanced Model"
              description="Final synthesis"
              color="#667eea"
            />
          </div>
        </div> */}

        {/* Footer */}
        <div style={{ textAlign: "center", color: "white", fontSize: "14px" }}>
          <p>Multi-Agent AI Content Verification System</p>
          <p style={{ marginTop: "8px", opacity: 0.8 }}>
            4 specialized models • 6 autonomous agents • Real-time protection
          </p>
        </div>
      </div>
    </div>
  );
}

// Component functions (StatCard, StatusItem, AlertCard, AgentCard) remain the same as before...
// (Copy from previous version)
function StatCard({ icon, value, label, color }: { icon: string; value: number; label: string; color: string }) {
  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        padding: "24px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
        borderLeft: `4px solid ${color}`,
        display: "flex",
        alignItems: "center",
        gap: "16px",
      }}
    >
      <div style={{ fontSize: "36px" }}>{icon}</div>
      <div>
        <div style={{ fontSize: "32px", fontWeight: "bold", color: "#333" }}>{value}</div>
        <div style={{ fontSize: "13px", color: "#666", marginTop: "4px" }}>{label}</div>
      </div>
    </div>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
      <span style={{ color: "#555", fontWeight: "500", fontSize: "14px" }}>{label}</span>
      <span style={{ fontWeight: "600", fontSize: "14px", color: "#4caf50" }}>{value}</span>
    </div>
  );
}

function AlertCard({ alert }: { alert: any }) {
  const getRiskColor = (level: string) => {
    if (level === "CRITICAL") return { bg: "#ffebee", text: "#c62828", border: "#f44336" };
    if (level === "HIGH") return { bg: "#fff3e0", text: "#e65100", border: "#ff9800" };
    return { bg: "#e3f2fd", text: "#1565c0", border: "#2196f3" };
  };

  const colors = getRiskColor(alert.risk_level);

  return (
    <div
      style={{
        background: colors.bg,
        borderLeft: `4px solid ${colors.border}`,
        borderRadius: "8px",
        padding: "16px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "24px" }}>
            {alert.risk_level === "CRITICAL" ? "🚨" : alert.risk_level === "HIGH" ? "⚠️" : "ℹ️"}
          </span>
          <div>
            <span style={{ fontWeight: "bold", color: colors.text }}>
              {alert.type === "message" ? "Suspicious Message" : "Suspicious Video"}
            </span>
            <span
              style={{
                marginLeft: "12px",
                padding: "4px 8px",
                fontSize: "11px",
                fontWeight: "bold",
                borderRadius: "4px",
                background: colors.border,
                color: "white",
              }}
            >
              {alert.risk_level}
            </span>
          </div>
        </div>
        <div style={{ fontSize: "12px", color: "#666" }}>Just now</div>
      </div>

      {alert.sender && (
        <div style={{ marginBottom: "8px", fontSize: "13px" }}>
          <strong>From:</strong> {alert.sender}{" "}
          <span
            style={{
              marginLeft: "8px",
              padding: "2px 8px",
              fontSize: "11px",
              background: "#e3f2fd",
              color: "#1976d2",
              borderRadius: "4px",
            }}
          >
            {alert.platform}
          </span>
        </div>
      )}

      <div style={{ fontSize: "14px", color: "#555", marginBottom: "12px" }}>
        "{alert.message || alert.title}"
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            border: "1px solid #e0e0e0",
            background: "white",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          📋 View Details
        </button>
        <button
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            border: "1px solid #e0e0e0",
            background: "white",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          ✓ Dismiss
        </button>
        <button
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            border: "1px solid #e0e0e0",
            background: "white",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          🚫 Report
        </button>
      </div>
    </div>
  );
}

function AgentCard({
  icon,
  name,
  model,
  description,
  color,
}: {
  icon: string;
  name: string;
  model: string;
  description: string;
  color: string;
}) {
  return (
    <div
      style={{
        background: `${color}10`,
        borderRadius: "12px",
        padding: "16px",
        borderLeft: `4px solid ${color}`,
      }}
    >
      <div style={{ fontSize: "24px", marginBottom: "8px" }}>{icon}</div>
      <div style={{ fontWeight: "bold", fontSize: "15px", color: "#333", marginBottom: "4px" }}>{name}</div>
      <div style={{ fontSize: "13px", color: "#666", marginBottom: "8px" }}>{model}</div>
      <div style={{ fontSize: "12px", color: "#999" }}>{description}</div>
    </div>
  );
}
