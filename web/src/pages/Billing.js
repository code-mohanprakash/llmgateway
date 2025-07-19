import React, { useState, useEffect } from 'react';
import { CreditCardIcon, CheckIcon, BoltIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const Billing = () => {
  const [currentPlan, setCurrentPlan] = useState('free');
  const [loading, setLoading] = useState(true);
  const [usageData, setUsageData] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    console.log('Billing component - Auth state:', { isAuthenticated, user: user?.email });
    
    if (isAuthenticated && user) {
      console.log('User is authenticated, fetching billing data...');
      fetchBillingData();
      fetchCurrentPlan();
    } else {
      console.log('User is not authenticated, setting loading to false');
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      console.log('Fetching billing data for user:', user?.email);
      
      const [usageRes, invoicesRes] = await Promise.all([
        api.get('/billing/usage'),
        api.get('/billing/invoices')
      ]);
      
      console.log('Billing data received:', usageRes.data);
      setUsageData(usageRes.data);
      setInvoices(invoicesRes.data || []);
    } catch (error) {
      console.error('Billing data fetch error:', error);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      
      // Completely suppress toast notifications for 401 errors
      if (error.response?.status !== 401) {
        let message = error.response?.data?.detail;
        if (!message && error.response?.data && typeof error.response.data === 'object') {
          if (Array.isArray(error.response.data)) {
            message = error.response.data.map(e => e.msg).join(', ');
          } else if (error.response.data.detail) {
            message = error.response.data.detail;
          } else {
            message = JSON.stringify(error.response.data);
          }
        }
        toast.error(message || 'Failed to load billing data');
      } else {
        console.log('Authentication failed - user needs to log in');
      }
      setUsageData(null);
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentPlan = async () => {
    try {
      const res = await api.get('/billing/current-plan');
      setCurrentPlan(res.data?.plan_id || 'free');
    } catch (error) {
      console.error('Failed to fetch current plan:', error);
      setCurrentPlan('free');
    }
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      monthlyPrice: 0,
      features: [
        '1,000 requests/month',
        '50,000 tokens/month',
        'Free models only',
        'Basic analytics'
      ]
    },
    {
      id: 'starter',
      name: 'Starter',
      monthlyPrice: 29,
      features: [
        '10,000 requests/month',
        '500,000 tokens/month',
        'All LLM providers',
        'Advanced analytics'
      ]
    },
    {
      id: 'professional',
      name: 'Professional',
      monthlyPrice: 99,
      features: [
        '100,000 requests/month',
        '5,000,000 tokens/month',
        'All providers + custom models',
        'Priority support'
      ],
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      monthlyPrice: 299,
      features: [
        'Unlimited requests & tokens',
        'All providers + custom models',
        '24/7 dedicated support',
        'Custom integrations'
      ]
    }
  ];

  const formatCurrency = (amount) => `$${amount.toFixed(2)}`;
  const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

  const UsageCard = ({ title, value, subtitle, icon: Icon, progress = null }) => (
    <div className="stat-card hover-lift">
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className="ml-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>
      {progress !== null && (
        <div className="progress-bg">
          <div 
            className="progress-bar" 
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </div>
  );

  const PlanCard = ({ plan, isCurrentPlan }) => {
    const handleUpgrade = async () => {
      try {
        const response = await api.post('/billing/upgrade', {
          plan_id: plan.id
        });
        toast.success('Plan upgraded successfully!');
        fetchCurrentPlan();
      } catch (error) {
        toast.error('Failed to upgrade plan. Please try again.');
      }
    };

    return (
      <div className={`clean-card p-6 relative ${
        isCurrentPlan 
          ? 'ring-2 ring-[#9B5967] bg-[#9B5967]/5' 
          : plan.popular 
            ? 'ring-2 ring-blue-200' 
            : ''
      }`}>
        {plan.popular && !isCurrentPlan && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span className="bg-[#9B5967] text-white px-3 py-1 rounded-full text-xs font-semibold">
              Popular
            </span>
          </div>
        )}
        {isCurrentPlan && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
              Current
            </span>
          </div>
        )}
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">{plan.name}</h3>
          <div className="mb-4">
            <span className="text-3xl font-bold text-gray-900">
              {plan.monthlyPrice === 0 ? 'Free' : `$${plan.monthlyPrice}`}
            </span>
            {plan.monthlyPrice > 0 && (
              <span className="text-gray-500 ml-1">/month</span>
            )}
          </div>
        </div>
        <ul className="space-y-3 mb-6">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <CheckIcon className="h-4 w-4 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              <span className="text-sm text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>
        <div className="text-center">
          {isCurrentPlan ? (
            <button className="btn-secondary w-full" disabled>
              Current Plan
            </button>
          ) : (
            <button className="w-full btn-primary" onClick={handleUpgrade}>
              {plan.monthlyPrice === 0 ? 'Downgrade' : 'Upgrade'}
            </button>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Billing & Usage</h1>
            <p className="text-gray-600">Loading your subscription and usage data...</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-gray-500"></div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Billing & Usage</h1>
          <p className="text-gray-600">
            Please log in to view your subscription and usage data.
          </p>
        </div>
        <div className="empty-state-card">
          <div className="empty-state-icon">🔐</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Authentication Required</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            You need to be logged in to view billing and usage information.
          </p>
          <a 
            href="/login" 
            className="btn-primary"
          >
            Log In
          </a>
        </div>
      </div>
    );
  }

  // If no usage data, show empty state
  if (!usageData) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Billing & Usage</h1>
          <p className="text-gray-600">
            No usage data available. Start making API requests to see your usage here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Billing & Usage</h1>
        <p className="text-gray-600">Manage your subscription and view usage</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UsageCard
          title="Tokens Used"
          value={usageData.current_period_tokens || 0}
          subtitle={`of ${usageData.monthly_token_limit || 0}`}
          icon={BoltIcon}
          progress={usageData.monthly_token_limit ? (usageData.current_period_tokens / usageData.monthly_token_limit) * 100 : 0}
        />
        <UsageCard
          title="Cost This Month"
          value={formatCurrency(usageData.current_period_cost || 0)}
          subtitle="Current billing period"
          icon={CreditCardIcon}
        />
        <UsageCard
          title="API Requests"
          value={usageData.current_period_requests || 0}
          subtitle="This billing period"
          icon={ArrowTrendingUpIcon}
          progress={usageData.monthly_request_limit ? (usageData.current_period_requests / usageData.monthly_request_limit) * 100 : 0}
        />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Pricing Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <PlanCard key={plan.id} plan={plan} isCurrentPlan={plan.id === currentPlan} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Billing;