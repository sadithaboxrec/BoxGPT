const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || data.message || data.error || "The request could not be completed.");
  }
  return response;
}

export async function getConversations() {
  const response = await request("/conversations");
  const data = await response.json();
  return data.conversations || [];
}

export async function getConversationHistory(threadId) {
  const response = await request(`/history/${encodeURIComponent(threadId)}`);
  const data = await response.json();
  return data.messages || [];
}

export async function uploadDocument(file, threadId) {
  const form = new FormData();
  form.append("file", file);
  form.append("thread_id", threadId);
  const response = await request("/upload", { method: "POST", body: form });
  const data = await response.json();
  if (!data.success) throw new Error(data.message || "Upload failed.");
  return data;
}

export async function streamChat({ message, threadId, model, onToken }) {
  const response = await request("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId, model }),
  });
  if (!response.body) throw new Error("Streaming is not supported by this browser.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";

  const consumeEvent = (event) => {
    const dataLines = event.split(/\r?\n/).filter((line) => line.startsWith("data:"));
    if (!dataLines.length) return;
    const payload = dataLines.map((line) => line.slice(5).trim()).join("\n");
    if (!payload || payload === "[DONE]") return;
    const data = JSON.parse(payload);
    if (data.error) throw new Error(data.error);
    if (data.token) {
      answer += data.token;
      onToken(answer, data.token);
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || "";
    events.forEach(consumeEvent);
  }
  buffer += decoder.decode();
  if (buffer.trim()) consumeEvent(buffer);
  return answer;
}
