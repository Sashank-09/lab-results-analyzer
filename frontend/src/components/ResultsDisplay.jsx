import React from "react";
import SeverityBadge from "./SeverityBadge";

function ResultCard({ result }) {
  return (
    <div className="result-card">
      <div className="result-header">
        <strong>{result.test_name}</strong>
        <SeverityBadge status={result.status} />
      </div>
      <p className="result-value">
        Value: {result.value} {result.unit || ""}
        {result.reference_low != null && result.reference_high != null && (
          <span className="ref-range">
            {" "}
            (Reference: {result.reference_low}–{result.reference_high})
          </span>
        )}
        {result.patient_id && <span className="patient-id"> · Patient {result.patient_id}</span>}
      </p>

      {result.error ? (
        <p className="error-text">{result.error}</p>
      ) : (
        <>
          <p className="explanation">{result.explanation}</p>
          {result.next_steps?.length > 0 && (
            <ul className="next-steps">
              {result.next_steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

function Section({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="section">
      <h3>{title} ({items.length})</h3>
      {items.map((r, i) => (
        <ResultCard key={i} result={r} />
      ))}
    </div>
  );
}

export default function ResultsDisplay({ results }) {
  if (!results) return null;

  const total =
    (results.critical?.length || 0) +
    (results.warning?.length || 0) +
    (results.normal?.length || 0) +
    (results.errors?.length || 0);

  if (total === 0) {
    return <p className="empty-state">No results yet. Submit lab data above to see the analysis.</p>;
  }

  return (
    <div className="results-display">
      <Section title="🚨 Critical" items={results.critical} />
      <Section title="⚠️ Warning" items={results.warning} />
      <Section title="✓ Normal" items={results.normal} />
      <Section title="⛔ Errors" items={results.errors} />
    </div>
  );
}
