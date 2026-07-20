import React from "react";

const CONFIG = {
  Critical: { emoji: "🚨", label: "Critical", className: "badge badge-critical" },
  Warning: { emoji: "⚠️", label: "Warning", className: "badge badge-warning" },
  Normal: { emoji: "✓", label: "Normal", className: "badge badge-normal" },
  Error: { emoji: "⛔", label: "Error", className: "badge badge-error" },
};

export default function SeverityBadge({ status }) {
  const cfg = CONFIG[status] || CONFIG.Error;
  return (
    <span className={cfg.className}>
      {cfg.emoji} {cfg.label}
    </span>
  );
}
