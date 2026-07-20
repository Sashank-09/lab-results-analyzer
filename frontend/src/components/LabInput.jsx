import React, { useState } from "react";
import Papa from "papaparse";

const EMPTY_ROW = { test_name: "", value: "", unit: "", patient_id: "" };

export default function LabInput({ onSubmit, loading }) {
  const [rows, setRows] = useState([{ ...EMPTY_ROW }]);
  const [csvError, setCsvError] = useState("");

  function updateRow(idx, field, val) {
    const next = [...rows];
    next[idx] = { ...next[idx], [field]: val };
    setRows(next);
  }

  function addRow() {
    setRows([...rows, { ...EMPTY_ROW }]);
  }

  function removeRow(idx) {
    setRows(rows.filter((_, i) => i !== idx));
  }

  function handleFormSubmit(e) {
    e.preventDefault();
    const labs = rows
      .filter((r) => r.test_name.trim() !== "")
      .map((r) => ({
        test_name: r.test_name.trim(),
        value: parseFloat(r.value),
        unit: r.unit || undefined,
        patient_id: r.patient_id || undefined,
      }));
    onSubmit(labs);
  }

  function handleCsvUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setCsvError("");

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const labs = results.data.map((r) => ({
            test_name: (r.test_name || r.Test || "").trim(),
            value: parseFloat(r.value || r.Value),
            unit: r.unit || r.Unit || undefined,
            patient_id: r.patient_id || r.PatientID || undefined,
          }));
          onSubmit(labs);
        } catch (err) {
          setCsvError("Could not parse CSV. Expected columns: test_name,value,unit,patient_id");
        }
      },
      error: () => setCsvError("Failed to read CSV file."),
    });
  }

  return (
    <div className="lab-input">
      <h2>Enter Lab Results</h2>

      <form onSubmit={handleFormSubmit}>
        {rows.map((row, idx) => (
          <div className="row" key={idx}>
            <input
              placeholder="Test name (e.g. Glucose)"
              value={row.test_name}
              onChange={(e) => updateRow(idx, "test_name", e.target.value)}
            />
            <input
              placeholder="Value"
              type="number"
              step="any"
              value={row.value}
              onChange={(e) => updateRow(idx, "value", e.target.value)}
            />
            <input
              placeholder="Unit (optional)"
              value={row.unit}
              onChange={(e) => updateRow(idx, "unit", e.target.value)}
            />
            <input
              placeholder="Patient ID (optional)"
              value={row.patient_id}
              onChange={(e) => updateRow(idx, "patient_id", e.target.value)}
            />
            {rows.length > 1 && (
              <button type="button" className="btn-remove" onClick={() => removeRow(idx)}>
                ✕
              </button>
            )}
          </div>
        ))}

        <div className="actions">
          <button type="button" onClick={addRow} className="btn-secondary">
            + Add Row
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </form>

      <div className="csv-upload">
        <label>
          Or upload a CSV (columns: test_name,value,unit,patient_id):
          <input type="file" accept=".csv" onChange={handleCsvUpload} disabled={loading} />
        </label>
        {csvError && <p className="error-text">{csvError}</p>}
      </div>
    </div>
  );
}
