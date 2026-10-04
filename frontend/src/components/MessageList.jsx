import { BrandMark } from "./Brand.jsx";

function TypingIndicator() {
  return <span className="inline-flex h-5 items-center gap-1" aria-label="BoxGPT is responding">
    <i className="animate-dot-1 size-1.5 rounded-full bg-pink-400" /><i className="animate-dot-2 size-1.5 rounded-full bg-pink-400" /><i className="animate-dot-3 size-1.5 rounded-full bg-pink-400" />
  </span>;
}

export default function MessageList({ messages, containerRef }) {
  return (
    <div ref={containerRef} className="h-full overflow-y-auto scroll-smooth">
      <div className="mx-auto w-full max-w-3xl px-4 pb-52 pt-8 sm:px-7">
        {messages.map((message) => <article key={message.id} className={`animate-message-in mb-6 flex items-start gap-2.5 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
          {message.role === "assistant" && <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-pink-100 text-pink-700"><BrandMark size={17} /></span>}
          <div className={`max-w-[88%] whitespace-pre-wrap break-words text-[13px] leading-7 sm:max-w-[78%] ${message.role === "user" ? "rounded-2xl rounded-br-sm border border-pink-100 bg-pink-50 px-4 py-2.5 text-pink-950" : "py-0.5 text-stone-700"}`}>
            {message.content || (message.streaming ? <TypingIndicator /> : null)}
          </div>
        </article>)}
      </div>
    </div>
  );
}
