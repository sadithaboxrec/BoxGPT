const shapes = {
  plus: <path d="M12 5v14M5 12h14" />,
  send: <><path d="m22 2-7 20-4-9-9-4Z" /><path d="M22 2 11 13" /></>,
  file: <><path d="m21.4 11.1-8.8 8.8a5.1 5.1 0 0 1-7.2-7.2l9.5-9.5a3.6 3.6 0 0 1 5.1 5.1l-9.6 9.6a2.1 2.1 0 0 1-3-3l8.8-8.8" /></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  boxingGlove: <><path d="M8.1 11.3V8.7a2.2 2.2 0 0 1 4.4 0v1.1-3a2.1 2.1 0 0 1 4.2 0v3-1a2 2 0 0 1 4 0v4.8a6.1 6.1 0 0 1-6.1 6.1h-3.2a5.6 5.6 0 0 1-4.7-2.5l-2.1-3.1a2.1 2.1 0 0 1 3.4-2.5l1.4 1.8v-2.1" /><path d="M8.3 17.1h8.9" /></>,
};

export default function Icon({ name, size = 18, className = "" }) {
  return <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>;
}
