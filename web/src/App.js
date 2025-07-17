import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
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

import Guides from './pages/Guides';
import Support from './pages/Support';
import About from './pages/About';

import Careers from './pages/Careers';
import Contact from './pages/Contact';
import Debug from './pages/Debug';
import Layout from './components/Layout';

function App() {
  return (
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
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;