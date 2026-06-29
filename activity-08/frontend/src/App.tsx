import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
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
import Login from "./pages/Login";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";

const queryClient = new QueryClient();

// Redirects users to /login if they don't have an active auth profile session
const AuthRequiredWrapper = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Toaster />
        <BrowserRouter>
          <Routes>
            {/* Full-Screen Login Route (No sidebar wrapper) */}
            <Route path="/login" element={<Login />} />

            {/* Authenticated Dashboard Router */}
            <Route
              path="*"
              element={
                <AuthRequiredWrapper>
                  <AppLayout>
                    <Routes>
                      {/* Public Pages */}
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/companies" element={<Companies />} />
                      <Route path="/companies/:companyId" element={<CompanyDetail />} />

                      {/* Student, Recruiter, and Admin Shared Pages */}
                      <Route 
                        path="/companies/:companyId/skills" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <CompanySkills />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/companies/:companyId/process" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <CompanyProcess />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/companies/:companyId/innovx" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <CompanyInnovX />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/hiring-skills" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <HiringSkills />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/hiring-process" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <HiringProcess />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/innovx" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <InnovX />
                          </ProtectedRoute>
                        } 
                      />

                      {/* Student & Admin Protected RAG & ML Services */}
                      <Route 
                        path="/chatbot" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Admin"]}>
                            <ChatbotPage />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/semantic-search" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Recruiter", "Admin"]}>
                            <SemanticSearchPage />
                          </ProtectedRoute>
                        } 
                      />
                      <Route 
                        path="/ml-analytics" 
                        element={
                          <ProtectedRoute allowedRoles={["Student", "Admin"]}>
                            <PredictiveAnalyticsPage />
                          </ProtectedRoute>
                        } 
                      />
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </AppLayout>
                </AuthRequiredWrapper>
              }
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

