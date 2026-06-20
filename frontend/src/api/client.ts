import type { VoicesResponse, SynthesizeRequest } from "../types/api";

const BASE = "/api";

export async function getVoices(): Promise<VoicesResponse> {
  const res = await fetch(`${BASE}/voices`);
  if (!res.ok) throw new Error(`GET /voices failed: ${res.status}`);
  return res.json();
}

export async function synthesizeSpeech(req: SynthesizeRequest): Promise<Blob> {
  const res = await fetch(`${BASE}/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json();
    throw Object.assign(new Error(err.message), { code: err.error, status: res.status });
  }
  return res.blob();
}
