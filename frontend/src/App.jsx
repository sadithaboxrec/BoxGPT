import { useCallback, useEffect, useRef, useState } from "react";
import { getConversationHistory, getConversations, streamChat, uploadDocument } from "./apiEndpoint.js";
import Composer from "./components/Composer.jsx";
import MessageList from "./components/MessageList.jsx";
import Sidebar from "./components/Sidebar.jsx";
import TopBar from "./components/TopBar.jsx";
import WelcomeScreen from "./components/WelcomeScreen.jsx";

function makeId() {
  return crypto.randomUUID();
}

function initialThread() {
  const saved = localStorage.getItem("boxgpt_thread_id");
  if (saved) return saved;
  const id = makeId();
  localStorage.setItem("boxgpt_thread_id", id);
  return id;
}

function detectTool(message) {
  const text = message.toLowerCase();
  if (/remember that|save this|store this|keep in memory|memorize/.test(text)) return "Saving a memory";
  if (/what do you remember|recall|my memory|remember about me/.test(text)) return "Searching memory";
  if (/document|pdf|file|uploaded|summarize|summary|according to|based on/.test(text)) return "Searching documents";
  if (/latest|current|today|now|recent|news|search web|web search|internet|online|price|version|update|2025|2026|who is|trending/.test(text)) return "Searching the web";
  if (/\d+\s*[+\-*/]\s*\d+|calculate|calculation|math|solve/.test(text)) return "Using calculator";
  return null;
}

export default function App() {
  const [threadId, setThreadId] = useState(initialThread);
  const [model, setModel] = useState(() => localStorage.getItem("boxgpt_model") || "gemini-2.5-flash");
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("Ready");
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState("");
  const messageContainerRef = useRef(null);
  const inputRef = useRef(null);

  const refreshConversations = useCallback(async () => {
    try {
      setConversations(await getConversations());
    } catch {
      // The API may be started separately from the Vite development server.
    }
  }, []);

  const loadConversation = useCallback(async (id) => {
    if (!id) {
      setSidebarOpen(false);
      return;
    }
    setThreadId(id);
    localStorage.setItem("boxgpt_thread_id", id);
    setError("");
    try {
      const history = await getConversationHistory(id);
      setMessages(history.map((message) => ({ ...message, id: makeId() })));
      setSidebarOpen(false);
    } catch (err) {
      setError(`${err.message}. Check that the FastAPI server is running.`);
      setMessages([]);
    }
  }, []);

  useEffect(() => {
    refreshConversations();
    loadConversation(threadId);
  }, []);

  useEffect(() => {
    const container = messageContainerRef.current;
    if (container) container.scrollTop = container.scrollHeight;
  }, [messages, status]);

  const newChat = () => {
    const id = makeId();
    setThreadId(id);
    localStorage.setItem("boxgpt_thread_id", id);
    setMessages([]);
    setError("");
    setSidebarOpen(false);
    inputRef.current?.focus();
  };

  const sendMessage = async (text = input) => {
    const content = text.trim();
    if (!content || busy || uploading) return;
    setInput("");
    setError("");
    setBusy(true);
    setMessages((current) => [...current,
      { id: makeId(), role: "user", content },
      { id: makeId(), role: "assistant", content: "", streaming: true },
    ]);
    setStatus(detectTool(content) || `Thinking with ${model}`);

    try {
      const answer = await streamChat({
        message: content,
        threadId,
        model,
        onToken: (fullAnswer) => {
          setStatus("Generating response");
          setMessages((current) => current.map((message) => message.streaming ? { ...message, content: fullAnswer } : message));
        },
      });
      if (!answer.trim()) {
        setMessages((current) => current.map((message) => message.streaming ? { ...message, content: "I couldn't generate a response. Please try again." } : message));
      }
    } catch (err) {
      const message = err.message || "Something went wrong. Please try again.";
      setError(message);
      setMessages((current) => current.map((item) => item.streaming ? { ...item, content: `Something went wrong: ${message}` } : item));
    } finally {
      setMessages((current) => current.map(({ streaming, ...message }) => message));
      setBusy(false);
      setStatus("Ready");
      refreshConversations();
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    setStatus("Adding document");
    setMessages((current) => [...current, { id: makeId(), role: "user", content: `Uploaded document: ${file.name}` }]);
    try {
      const result = await uploadDocument(file, threadId);
      setMessages((current) => [...current, { id: makeId(), role: "assistant", content: `${result.message}\nYou can now ask questions about this document.` }]);
      refreshConversations();
    } catch (err) {
      setError(err.message || "Upload failed.");
      setMessages((current) => current.filter((message) => message.content !== `Uploaded document: ${file.name}`));
    } finally {
      setUploading(false);
      setStatus("Ready");
      event.target.value = "";
    }
  };

  const handleSuggestion = (prompt) => {
    setInput(prompt);
    inputRef.current?.focus();
  };

  const handleModelChange = (nextModel) => {
    setModel(nextModel);
    localStorage.setItem("boxgpt_model", nextModel);
  };

  return (
    <div className="flex h-dvh min-h-[580px] w-full overflow-hidden bg-[#fffafd] text-stone-800">
      <Sidebar conversations={conversations} threadId={threadId} open={sidebarOpen} onNewChat={newChat} onSelectChat={loadConversation} />
      <main className="relative flex min-w-0 flex-1 flex-col bg-[radial-gradient(ellipse_at_70%_-15%,#fff0f6_0%,transparent_42%),#fffafd]">
        <TopBar status={status} onMenu={() => setSidebarOpen(true)} />
        <section className={`min-h-0 flex-1 overflow-y-auto ${messages.length === 0 ? "flex items-center justify-center px-5 pb-40 pt-8 sm:pb-48" : ""}`}>
          {messages.length === 0
            ? <WelcomeScreen onSuggestion={handleSuggestion} />
            : <MessageList messages={messages} containerRef={messageContainerRef} />}
        </section>
        <Composer input={input} setInput={setInput} model={model} onModelChange={handleModelChange} onSend={() => sendMessage()} onUpload={handleUpload} busy={busy} uploading={uploading} inputRef={inputRef} />
        {error && <div role="alert" className="absolute bottom-[104px] left-3 right-3 z-20 mx-auto max-w-3xl rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-xs text-rose-800 shadow-sm sm:bottom-[110px] sm:left-6 sm:right-6">{error}</div>}
      </main>
    </div>
  );
}
