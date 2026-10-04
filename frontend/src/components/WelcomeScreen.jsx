import Icon from "./Icon.jsx";
import { BrandMark } from "./Brand.jsx";

const suggestions = [
  { icon: "⌕", title: "Search the web", prompt: "Search the web for the latest AI agent news." },
  { icon: "▤", title: "Ask about a document", prompt: "Summarize the document I uploaded." },
  { icon: "♡", title: "Save a memory", prompt: "Remember that my channel name is dswithbappy." },
  { icon: "＋", title: "Do a calculation", prompt: "Calculate 125 * 48 / 6" },
];

export default function WelcomeScreen({ onSuggestion }) {
  return (
    <div className="mx-auto w-full max-w-xl animate-message-in text-center">
      <div className="mx-auto mb-6 grid size-14 place-items-center rounded-2xl bg-gradient-to-br from-pink-400 to-pink-700 text-white shadow-lg shadow-pink-200/70">
        <BrandMark size={29} />
      </div>
      <p className="mb-2 text-[10px] font-bold tracking-[.2em] text-pink-700/70">A LITTLE HELP, RIGHT ON TIME</p>
      <h1 className="font-sans text-3xl font-semibold tracking-tight text-stone-800 sm:text-[34px]">What’s on your mind?</h1>
      <p className="mx-auto mb-7 mt-3 max-w-md text-sm leading-6 text-stone-500">Ask a question, explore an idea, or pick up where you left off.</p>
      <div className="grid grid-cols-1 gap-2.5 text-left min-[440px]:grid-cols-2">
        {suggestions.map((suggestion) => <button key={suggestion.title} onClick={() => onSuggestion(suggestion.prompt)} className="group flex min-h-14 items-center gap-3 rounded-xl border border-stone-200/90 bg-white/90 px-3 transition hover:-translate-y-0.5 hover:border-pink-200 hover:bg-pink-50/70 hover:shadow-sm focus-visible:outline-2 focus-visible:outline-pink-500">
          <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-pink-50 text-base text-pink-700">{suggestion.icon}</span>
          <span className="text-xs font-medium text-stone-600">{suggestion.title}</span>
          <Icon name="chevron" size={16} className="ml-auto text-stone-300 transition group-hover:translate-x-0.5 group-hover:text-pink-500" />
        </button>)}
      </div>
    </div>
  );
}
