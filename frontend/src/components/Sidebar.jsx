import Brand from "./Brand.jsx";
import Icon from "./Icon.jsx";

export default function Sidebar({ conversations, threadId, open, onNewChat, onSelectChat }) {
  return (
    <>
      {open && <button className="fixed inset-0 z-30 bg-stone-950/30 md:hidden" aria-label="Close navigation" onClick={() => onSelectChat(null)} />}
      <aside className={`fixed inset-y-0 left-0 z-40 flex w-[276px] flex-col border-r border-pink-100 bg-white px-4 py-6 transition-transform duration-200 md:static md:z-auto md:w-[258px] md:shrink-0 md:translate-x-0 ${open ? "translate-x-0 shadow-2xl shadow-stone-900/10" : "-translate-x-full"}`}>
        <Brand onClick={onNewChat} />
        <button onClick={onNewChat} className="mt-9 flex h-11 items-center gap-2.5 rounded-xl border border-pink-200 bg-pink-50/80 px-3.5 text-sm font-semibold text-pink-800 transition hover:border-pink-300 hover:bg-pink-100 focus-visible:outline-2 focus-visible:outline-pink-500">
          <Icon name="plus" size={17} /> New chat
        </button>
        <p className="mb-2 mt-8 px-2 text-[10px] font-bold tracking-[.16em] text-stone-400">RECENT CHATS</p>
        <nav className="flex-1 space-y-1 overflow-y-auto" aria-label="Recent conversations">
          {conversations.length === 0 ? <p className="px-2 py-3 text-xs text-stone-400">Your chats will appear here</p> : conversations.map((conversation) => (
            <button key={conversation.thread_id} onClick={() => onSelectChat(conversation.thread_id)} title={conversation.title} className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-xs transition ${conversation.thread_id === threadId ? "bg-pink-50 font-semibold text-pink-800" : "text-stone-600 hover:bg-stone-50"}`}>
              <span className={`size-1.5 shrink-0 rounded-full ${conversation.thread_id === threadId ? "bg-pink-500" : "border border-pink-300"}`} />
              <span className="truncate">{conversation.title || "New chat"}</span>
            </button>
          ))}
        </nav>
        <div className="flex items-center gap-2 border-t border-stone-100 px-2 pt-4 text-[11px] text-stone-400">
          <span className="size-1.5 rounded-full bg-emerald-400 ring-4 ring-emerald-50" /> Your personal AI workspace
        </div>
      </aside>
    </>
  );
}
