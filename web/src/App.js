import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import APIKeys from './pages/APIKeys';
import Team from './pages/Team';
import Billing from './pages/Billing';
import Settings from './pages/Settings';
import Landing from './pages/Landing';
import Models from './pages/Models';
import Documentation from './pages/Documentation';
import Pricing from './pages/Pricing';
import RBAC from './pages/RBAC';
import APIPlayground from './pages/APIPlayground';
import ABTesting from './pages/ABTesting';
import AdvancedRouting from './pages/AdvancedRouting';
import CostOptimization from './pages/CostOptimization';
import Orchestration from './pages/Orchestration';
import Monitoring from './pages/Monitoring';
import Product from './pages/Product';
import IntelligentRouting from './pages/IntelligentRouting';
import EnterpriseFeatures from './pages/EnterpriseFeatures';
import Security from './pages/Security';
import DeveloperExperience from './pages/DeveloperExperience';

import Guides from './pages/Guides';
import Support from './pages/Support';
import About from './pages/About';

import Careers from './pages/Careers';
import Contact from './pages/Contact';
import Debug from './pages/Debug';
import Layout from './components/Layout';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="App">
            <Toaster position="top-right" />
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/debug" element={<Debug />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/docs" element={<Documentation />} />

            <Route path="/guides" element={<Guides />} />
            <Route path="/support" element={<Support />} />
            <Route path="/about" element={<About />} />

            <Route path="/careers" element={<Careers />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/models" element={<Models />} />
            <Route path="/product" element={<Product />} />
            <Route path="/product/intelligent-routing" element={<IntelligentRouting />} />
            <Route path="/product/cost-optimization" element={<CostOptimization />} />
            <Route path="/product/enterprise-features" element={<EnterpriseFeatures />} />
            <Route path="/product/orchestration" element={<Orchestration />} />
            <Route path="/product/monitoring" element={<Monitoring />} />
            <Route path="/product/security" element={<Security />} />
            <Route path="/product/developer-experience" element={<DeveloperExperience />} />
            
            {/* Protected Dashboard Routes */}
            <Route
              path="/dashboard/*"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="api-keys" element={<APIKeys />} />
              <Route path="team" element={<Team />} />
              <Route path="billing" element={<Billing />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* Enterprise Routes */}
            <Route
              path="/rbac"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<RBAC />} />
            </Route>

            <Route
              path="/api-playground"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<APIPlayground />} />
            </Route>
            <Route
              path="/ab-testing"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<ABTesting />} />
            </Route>
            
            <Route
              path="/advanced-routing"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<AdvancedRouting />} />
            </Route>
            
            <Route
              path="/cost-optimization"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<CostOptimization />} />
            </Route>
            
            <Route
              path="/orchestration"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Orchestration />} />
            </Route>
            
            <Route
              path="/monitoring"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Monitoring />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;