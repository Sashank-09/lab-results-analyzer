import React, { useState } from "react";
import LabInput from "./components/LabInput";
import ResultsDisplay from "./components/ResultsDisplay";
import { analyzeLabs } from "./api";

export default function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(labs) {
    if (!labs || labs.length === 0) {
      setError("Please enter at least one lab result.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const data = await analyzeLabs(labs);
      setResults(data);
    } catch (err) {
      setError(err.message || "Something went wrong analyzing the labs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Clinical Lab Results Analyzer</h1>
        <p className="subtitle">
          AI-assisted classification with explainable, clinically relevant reasoning.
        </p>
      </header>

      <LabInput onSubmit={handleSubmit} loading={loading} />

      {error && <p className="error-text banner">{error}</p>}

      <ResultsDisplay results={results} />
    </div>
  );
}
