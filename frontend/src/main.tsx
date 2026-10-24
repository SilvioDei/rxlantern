import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import "@fontsource-variable/fraunces";
import "@fontsource/atkinson-hyperlegible/400.css";
import "@fontsource/atkinson-hyperlegible/700.css";
import "./styles.css";
import { AppProvider } from "./state";
import { Footer, Header } from "./components/Layout";
import { AuthModal } from "./components/Forms";
import { Home } from "./pages/Home";
import { Pharmacies } from "./pages/Pharmacies";
import { PharmacyPage } from "./pages/PharmacyPage";
import { Shortages } from "./pages/Shortages";
import { Vaccines } from "./pages/Vaccines";
import { Admin } from "./pages/Admin";

function ScrollTop() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return null;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AppProvider>
        <ScrollTop />
        <Header />
        <main id="main" tabIndex={-1}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/pharmacies" element={<Pharmacies />} />
            <Route path="/pharmacies/:id" element={<PharmacyPage />} />
            <Route path="/shortages" element={<Shortages />} />
            <Route path="/vaccines" element={<Vaccines />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
        <Footer />
        <AuthModal />
      </AppProvider>
    </BrowserRouter>
  </StrictMode>,
);
