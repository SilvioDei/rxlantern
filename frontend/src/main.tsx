import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import "@fontsource-variable/fraunces";
import "@fontsource/atkinson-hyperlegible/400.css";
import "@fontsource/atkinson-hyperlegible/700.css";
import "./styles.css";
import { AppProvider } from "./state";
import { Footer, Header, Toast } from "./components/Layout";
import { AuthModal, ReportFormHost, ReviewFormHost } from "./components/Forms";
import { Home } from "./pages/Home";
import { Results } from "./pages/Results";
import { PrintSummary } from "./pages/PrintSummary";
import { Pharmacies } from "./pages/Pharmacies";
import { PharmacyPage } from "./pages/PharmacyPage";
import { Shortages } from "./pages/Shortages";
import { Vaccines } from "./pages/Vaccines";
import { VaccineResults } from "./pages/VaccineResults";
import { Community } from "./pages/Community";
import { AboutPage } from "./pages/About";
import { Admin } from "./pages/Admin";
import { OtherMedicine } from "./pages/OtherMedicine";
import { MyList } from "./pages/MyList";
import { SendHere } from "./pages/SendHere";
import { LanguageCard } from "./pages/LanguageCard";
import { ForPharmacies } from "./pages/ForPharmacies";
import { TransferHost } from "./components/Journey";

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
            <Route path="/results" element={<Results />} />
            <Route path="/print" element={<PrintSummary />} />
            <Route path="/pharmacies" element={<Pharmacies />} />
            <Route path="/pharmacies/:id" element={<PharmacyPage />} />
            <Route path="/shortages" element={<Shortages />} />
            <Route path="/vaccines" element={<Vaccines />} />
            <Route path="/vaccine-results" element={<VaccineResults />} />
            <Route path="/community" element={<Community />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/other-medicine" element={<OtherMedicine />} />
            <Route path="/my-list" element={<MyList />} />
            <Route path="/send-here/:id" element={<SendHere />} />
            <Route path="/language-card" element={<LanguageCard />} />
            <Route path="/for-pharmacies" element={<ForPharmacies />} />
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
        <Footer />
        <Toast />
        <AuthModal />
        <ReportFormHost />
        <ReviewFormHost />
        <TransferHost />
      </AppProvider>
    </BrowserRouter>
  </StrictMode>,
);
