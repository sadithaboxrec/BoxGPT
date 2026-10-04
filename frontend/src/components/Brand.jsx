import Icon from "./Icon.jsx";

export function BrandMark({ size = 18, className = "" }) {
  return <Icon name="boxingGlove" size={size} className={className} />;
}

export default function Brand({ onClick }) {
  return (
    <button onClick={onClick} className="flex items-center gap-2.5 rounded-lg px-2 text-left" aria-label="BoxGPT new chat">
      <span className="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-pink-400 to-pink-700 text-white shadow-md shadow-pink-200/70">
        <BrandMark size={22} />
      </span>
      <span className="font-sans text-lg font-extrabold tracking-tight text-stone-800">BoxGPT</span>
    </button>
  );
}
