import React, { useState, useEffect } from 'react';
import { CreditCardIcon, CheckIcon, BoltIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';

const Billing = () => {
  console.log('Billing component rendering');
  const [currentPlan, setCurrentPlan] = useState('free');
  const [loading, setLoading] = useState(true);
  const [usageData, setUsageData] = useState(null);
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    console.log('Billing useEffect triggered');
    fetchBillingData();
    fetchCurrentPlan();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      console.log('Fetching billing data...');
      
      const [usageRes, invoicesRes] = await Promise.all([
        api.get('/billing/usage'),
        api.get('/billing/invoices')
      ]);
      
      console.log('Usage response:', usageRes.data);
      console.log('Invoices response:', invoicesRes.data);
      
      setUsageData(usageRes.data);
      setInvoices(invoicesRes.data || []);
      
    } catch (error) {
      console.error('Billing data fetch error:', error);
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
      
      // Set real empty state, not fake data
      setUsageData({
        current_period_requests: 0,
        current_period_tokens: 0,
        current_period_cost: 0,
        monthly_token_limit: 0,
        monthly_request_limit: 0,
        top_models: []
      });
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
        console.error('Failed to upgrade plan:', error);
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

  // Default usage fallback - real zero state
  const defaultUsage = {
    current_period_requests: 0,
    current_period_tokens: 0,
    current_period_cost: 0,
    monthly_token_limit: 0,
    monthly_request_limit: 0,
    top_models: []
  };

  // Use fallback if usageData is null/undefined
  const usageSafe = usageData || defaultUsage;
  const invoicesSafe = invoices || [];
  const hasUsage = usageSafe && (usageSafe.current_period_requests > 0 || usageSafe.current_period_cost > 0);

  if (loading) {
    console.log('Billing: Showing loading state');
    return (
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Billing & Usage</h1>
            <p className="text-gray-600 mt-2">Manage your subscription and view usage analytics</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="stat-card animate-pulse">
              <div className="h-24 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
        
        <div className="flex items-center justify-center h-64">
          <div className="spinner w-12 h-12"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Billing & Usage</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and view usage</p>
        </div>
      </div>

      {/* Current Usage */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UsageCard
          title="Tokens Used"
          value={usageSafe.current_period_tokens?.toLocaleString() || '0'}
          subtitle={`of ${usageSafe.monthly_token_limit?.toLocaleString() || 'unlimited'}`}
          icon={BoltIcon}
          progress={usageSafe.monthly_token_limit ? (usageSafe.current_period_tokens / usageSafe.monthly_token_limit) * 100 : null}
        />
        
        <UsageCard
          title="Cost This Month"
          value={formatCurrency(usageSafe.current_period_cost || 0)}
          subtitle="Current billing period"
          icon={CreditCardIcon}
        />
        
        <UsageCard
          title="API Requests"
          value={usageSafe.current_period_requests?.toLocaleString() || '0'}
          subtitle="This billing period"
          icon={ArrowTrendingUpIcon}
        />
      </div>

      {/* Pricing Plans */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Pricing Plans</h2>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              isCurrentPlan={plan.id === currentPlan}
            />
          ))}
        </div>
      </div>

      {/* Usage Breakdown */}
      {hasUsage && usageSafe?.top_models && usageSafe.top_models.length > 0 && (
        <div className="clean-card overflow-hidden">
          <div className="px-6 py-4 table-header">
            <h3 className="text-lg font-semibold text-gray-900">Model Usage</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {usageSafe.top_models.map((model, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <span className="text-sm font-medium text-gray-900">{model.model_id}</span>
                  <div className="flex items-center space-x-6">
                    <span className="text-sm text-gray-600">{model.request_count} requests</span>
                    <span className="text-sm font-semibold text-gray-900">{formatCurrency(model.cost)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Billing;