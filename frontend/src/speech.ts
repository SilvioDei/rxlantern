// Browser speech: read aloud (speech synthesis) and voice questions (speech recognition). No servers involved.
import type { Lang } from "./i18n";

const voiceLang = (lang: Lang) => (lang === "es" ? "es-US" : "en-US");

export function canSpeak(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

export function speak(text: string, lang: Lang, onEnd?: () => void): void {
  if (!canSpeak()) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = voiceLang(lang);
  u.rate = 0.95;
  u.onend = () => onEnd?.();
  u.onerror = () => onEnd?.();
  window.speechSynthesis.speak(u);
}

export function stopSpeaking(): void {
  if (canSpeak()) window.speechSynthesis.cancel();
}

type Recognition = {
  lang: string; interimResults: boolean; maxAlternatives: number;
  onresult: (e: any) => void; onend: () => void; onerror: () => void; start: () => void; stop: () => void;
};

export function recognitionSupported(): boolean {
  return typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
}

export function listen(lang: Lang, onText: (text: string) => void, onDone: () => void): Recognition | null {
  const W = window as any;
  const Rec = W.SpeechRecognition || W.webkitSpeechRecognition;
  if (!Rec) return null;
  const r: Recognition = new Rec();
  r.lang = voiceLang(lang);
  r.interimResults = false;
  r.maxAlternatives = 1;
  r.onresult = (e: any) => onText(e.results?.[0]?.[0]?.transcript ?? "");
  r.onend = onDone;
  r.onerror = onDone;
  r.start();
  return r;
}
