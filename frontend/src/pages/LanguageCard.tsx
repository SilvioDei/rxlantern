// Language help card: one sentence in Chinese (Traditional and Simplified), Haitian Creole, and Spanish, with the
// English underneath, to show at the pharmacy counter. Printable. Translations are labeled as not yet reviewed.
import { useApp } from "../state";
import { ReadAloud } from "../components/Bits";

const ENGLISH = "I need help in my language, please. Can someone help me or call an interpreter?";
// Not yet reviewed by native speakers (the page says so).
const LINES: { lang: string; label: string; text: string }[] = [
  { lang: "zh-Hant", label: "中文（繁體） · Chinese (Traditional)", text: "我需要用我的語言獲得幫助。可以請人幫我，或幫我打電話給口譯員嗎？" },
  { lang: "zh-Hans", label: "中文（简体） · Chinese (Simplified)", text: "我需要用我的语言获得帮助。可以请人帮我，或帮我打电话给口译员吗？" },
  { lang: "ht", label: "Kreyòl ayisyen · Haitian Creole", text: "Mwen bezwen èd nan lang mwen, tanpri. Èske yon moun ka ede m oswa rele yon entèprèt pou mwen?" },
  { lang: "es", label: "Español · Spanish", text: "Necesito ayuda en mi idioma, por favor. ¿Alguien me puede ayudar o llamar a un intérprete?" },
];

export function LanguageCard() {
  const { t, lang } = useApp();
  return (
    <div className="language-card-page print-page">
      <h1 className="no-print">{t("langCardTitle")}</h1>
      <p className="lead no-print">{t("langCardIntro")}</p>
      <section className="language-card" aria-label={t("langCardTitle")}>
        {LINES.map((l) => (
          <div key={l.lang} className="lc-line">
            <p className="lc-label">{l.label}</p>
            <p className="lc-text" lang={l.lang}>{l.text}</p>
            <p className="lc-english" lang="en">{ENGLISH}</p>
          </div>
        ))}
        <p className="lc-warn"><span aria-hidden="true">⚠</span> {t("langCardWarn")}{lang !== "en" && <span lang="en"> (Translation not yet reviewed by a native speaker.)</span>}</p>
      </section>
      <div className="card-actions no-print">
        <button type="button" className="btn primary big" onClick={() => window.print()}><span aria-hidden="true">🖨</span> {t("langCardPrint")}</button>
        <ReadAloud text={ENGLISH} />
      </div>
    </div>
  );
}
