import { useRef } from "react";
import Icon from "./Icon.jsx";

const MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"];

export default function Composer({ input, setInput, model, onModelChange, onSend, onUpload, busy, uploading, inputRef }) {
  const fileRef = useRef(null);
  return (
    <footer className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#fffafd] via-[#fffafd]/95 to-transparent px-3 pb-3 pt-10 sm:px-6 sm:pb-5">
      <div className="mx-auto flex min-h-[60px] w-full max-w-3xl items-end gap-1.5 rounded-2xl border border-stone-200 bg-white p-2 shadow-[0_10px_32px_rgba(84,31,58,.08)] transition focus-within:border-pink-300 focus-within:ring-4 focus-within:ring-pink-100/70 sm:gap-2">
        <input ref={fileRef} type="file" className="sr-only" accept=".pdf,.docx,.txt,.md,.py,.csv" onChange={onUpload} />
        <button type="button" disabled={busy || uploading} onClick={() => fileRef.current?.click()} aria-label="Upload a document" title="Upload a document" className="grid size-9 shrink-0 place-items-center rounded-xl text-stone-400 transition hover:bg-pink-50 hover:text-pink-700 disabled:opacity-40">
          <Icon name="file" size={19} />
        </button>
        <textarea ref={inputRef} value={input} rows={1} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); onSend(); } }} placeholder="Message BoxGPT…" aria-label="Message BoxGPT" className="max-h-36 min-h-9 min-w-0 flex-1 resize-none bg-transparent px-1 py-2.5 text-xs leading-5 text-stone-800 outline-none placeholder:text-stone-400" />
        <select aria-label="Choose a model" value={model} onChange={(event) => onModelChange(event.target.value)} className="h-9 max-w-[124px] shrink-0 rounded-lg border border-stone-200 bg-stone-50 px-2 text-[10px] text-stone-600 outline-none focus:border-pink-300 sm:max-w-none sm:text-[11px]">
          {MODELS.map((item) => <option key={item} value={item}>{item.replace("gemini-", "Gemini ")}</option>)}
        </select>
        <button type="button" aria-label="Send message" disabled={!input.trim() || busy || uploading} onClick={onSend} className="grid size-9 shrink-0 place-items-center rounded-xl bg-pink-600 text-white shadow-md shadow-pink-200 transition hover:bg-pink-700 disabled:bg-stone-200 disabled:text-stone-400 disabled:shadow-none">
          <Icon name="send" size={16} />
        </button>
      </div>
      <p className="mt-2.5 text-center text-[10px] text-stone-400">{uploading ? "Adding your document…" : "BoxGPT can make mistakes. Check important info."}</p>
    </footer>
  );
}
