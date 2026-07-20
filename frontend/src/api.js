const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export async function analyzeLabs(labs) {
  const res = await fetch(`${API_BASE}/analyze_labs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ labs }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }

  return res.json();
}
