import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import Companies from "./pages/Companies";
import CompanyDetail from "./pages/CompanyDetail";
import CompanySkills from "./pages/CompanySkills";
import CompanyProcess from "./pages/CompanyProcess";
import CompanyInnovX from "./pages/CompanyInnovX";
import HiringSkills from "./pages/HiringSkills";
import HiringProcess from "./pages/HiringProcess";
import InnovX from "./pages/InnovX";
import ChatbotPage from "./pages/ChatbotPage";
import SemanticSearchPage from "./pages/SemanticSearchPage";
import PredictiveAnalyticsPage from "./pages/PredictiveAnalyticsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/companies/:companyId" element={<CompanyDetail />} />
            <Route path="/companies/:companyId/skills" element={<CompanySkills />} />
            <Route path="/companies/:companyId/process" element={<CompanyProcess />} />
            <Route path="/companies/:companyId/innovx" element={<CompanyInnovX />} />
            <Route path="/hiring-skills" element={<HiringSkills />} />
            <Route path="/hiring-process" element={<HiringProcess />} />
            <Route path="/innovx" element={<InnovX />} />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="/semantic-search" element={<SemanticSearchPage />} />
            <Route path="/ml-analytics" element={<PredictiveAnalyticsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
