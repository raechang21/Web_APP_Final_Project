import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Chatbot from "@/pages/Chatbot";
import DeepAnalysis from "@/pages/DeepAnalysis";
import Diagnostic from "@/pages/Diagnostic";
import DarkTriadIntro from "@/pages/DarkTriadIntro";
import DarkTriadTest from "@/pages/DarkTriadTest";
import BigFiveTest from "@/pages/BigFiveTest";
import MbtiInput from "@/pages/MbtiInput";
import NotFound from "@/pages/NotFound";
import Results from "@/pages/Results";
import Welcome from "@/pages/Welcome";
import ZodiacSelection from "@/pages/ZodiacSelection";
import { useSessionStore } from "@/store/session";

export default function App() {
  const hydrate = useSessionStore((state) => state.hydrate);
  const hydrated = useSessionStore((state) => state.hydrated);
  const status = useSessionStore((state) => state.status);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  if (!hydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center text-stone-500">
        讀取 session 中...
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<Welcome />} />
      <Route path="/mbti" element={<MbtiInput />} />
      <Route path="/big-five" element={<BigFiveTest />} />
      <Route path="/zodiac" element={<ZodiacSelection />} />
      <Route path="/dark-triad-intro" element={<DarkTriadIntro />} />
      <Route path="/dark-triad" element={<DarkTriadTest />} />
      <Route path="/results" element={<Results />} />
      <Route path="/deep-analysis" element={<DeepAnalysis />} />
      <Route path="/chatbot" element={<Chatbot />} />
      <Route path="/diagnostic" element={<Diagnostic />} />
      <Route path="/welcome" element={<Navigate to="/" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
