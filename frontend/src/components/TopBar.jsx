import Icon from "./Icon.jsx";

export default function TopBar({ status, onMenu }) {
  return (
    <header className="z-10 flex h-[62px] shrink-0 items-center border-b border-pink-100/80 bg-white/75 px-4 backdrop-blur-lg sm:h-[66px] sm:px-8">
      <button onClick={onMenu} className="mr-2 grid size-9 place-items-center rounded-lg text-stone-500 hover:bg-stone-100 md:hidden" aria-label="Open navigation"><Icon name="menu" /></button>
      <div className="mr-auto text-[13px] font-semibold text-stone-700"><span className="md:hidden">BoxGPT</span><span className="hidden md:inline">Your AI workspace</span></div>
      <div className="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-1.5 text-[10px] text-stone-500 sm:text-[11px]">
        <span className={`size-1.5 rounded-full ${status === "Ready" ? "bg-emerald-400" : "animate-pulse bg-pink-500"}`} />{status}
      </div>
    </header>
  );
}
