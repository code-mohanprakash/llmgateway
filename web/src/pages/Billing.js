import React, { useState, useEffect } from 'react';
import { CreditCardIcon, ClockIcon, CheckIcon, XMarkIcon, ArrowTrendingUpIcon, BoltIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';

const Billing = () => {
  console.log('Billing component rendering');
  const [currentPlan, setCurrentPlan] = useState('professional');
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [loading, setLoading] = useState(true);
  const [usageData, setUsageData] = useState(null);
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    console.log('Billing useEffect triggered');
    fetchBillingData();
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
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      description: 'Perfect for trying out our LLM Gateway',
      monthlyPrice: 0,
      yearlyPrice: 0,
      features: [
        '1,000 requests/month',
        '50,000 tokens/month',
        'Free models only (HuggingFace, Ollama)',
        'Basic analytics',
        'Community support',
        'Standard uptime'
      ],
      limitations: [
        'Premium models locked',
        'Limited to 1 API key',
        'No priority support',
        'No team features'
      ],
      color: 'gray',
      modelAccess: ['huggingface', 'ollama']
    },
    {
      id: 'starter',
      name: 'Starter',
      description: 'For individual developers and small projects',
      monthlyPrice: 29,
      yearlyPrice: 290,
      features: [
        '10,000 requests/month',
        '500,000 tokens/month',
        'All LLM providers',
        'Advanced analytics',
        'Priority support',
        '99.9% uptime SLA',
        'Team collaboration',
        'API key management'
      ],
      limitations: [
        'Limited custom model training'
      ],
      color: 'blue',
      modelAccess: ['all']
    },
    {
      id: 'professional',
      name: 'Professional',
      description: 'For growing teams and businesses',
      monthlyPrice: 99,
      yearlyPrice: 990,
      features: [
        '100,000 requests/month',
        '5,000,000 tokens/month',
        'All LLM providers + custom models',
        'Advanced analytics & reporting',
        'Priority support',
        '99.95% uptime SLA',
        'Custom rate limits',
        'Advanced team features',
        'Custom integrations'
      ],
      limitations: [],
      color: 'blue',
      popular: true,
      modelAccess: ['all']
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large organizations with advanced needs',
      monthlyPrice: 299,
      yearlyPrice: 2990,
      features: [
        'Unlimited requests & tokens',
        'All providers + custom models',
        '24/7 dedicated support',
        'Custom analytics & reporting',
        '99.99% uptime SLA',
        'Custom integrations',
        'Advanced security features',
        'On-premise deployment',
        'Custom contracts',
        'Dedicated account manager'
      ],
      limitations: [],
      color: 'blue',
      modelAccess: ['all']
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
    const price = billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;
    const savings = billingCycle === 'yearly' ? (plan.monthlyPrice * 12 - plan.yearlyPrice) : 0;

    return (
      <div className={`clean-card p-6 hover-lift relative ${
        isCurrentPlan 
          ? 'ring-2 ring-blue-500 bg-blue-50' 
          : plan.popular 
            ? 'ring-2 ring-blue-200' 
            : ''
      }`}>
        {plan.popular && !isCurrentPlan && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
              Most Popular
            </span>
          </div>
        )}
        {isCurrentPlan && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
              Current Plan
            </span>
          </div>
        )}

        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
          <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
          
          <div className="mb-4">
            <span className="text-4xl font-bold text-gray-900">
              {price === 0 ? 'Free' : formatCurrency(price)}
            </span>
            {price > 0 && (
              <span className="text-gray-500 ml-1">
                /{billingCycle === 'monthly' ? 'month' : 'year'}
              </span>
            )}
            {savings > 0 && (
              <div className="text-sm text-green-600 mt-1 font-medium">
                Save {formatCurrency(savings)} annually
              </div>
            )}
          </div>
        </div>

        <ul className="space-y-3 mb-6">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <CheckIcon className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              <span className="text-sm text-gray-700">{feature}</span>
            </li>
          ))}
          {plan.limitations.map((limitation, index) => (
            <li key={index} className="flex items-start">
              <XMarkIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-3 flex-shrink-0" />
              <span className="text-sm text-gray-500">{limitation}</span>
            </li>
          ))}
        </ul>

        <div className="text-center">
          {isCurrentPlan ? (
            <button className="btn-secondary w-full" disabled>
              Current Plan
            </button>
          ) : (
            <button className={`w-full ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}>
              {price === 0 ? 'Downgrade to Free' : 'Upgrade Plan'}
            </button>
          )}
        </div>
      </div>
    );
  };

  // Default usage fallback
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

  console.log('Billing: Rendering main content, usageData:', usageData, 'invoices:', invoices);
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Billing & Usage</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and view usage analytics</p>
        </div>
      </div>

      {/* Current Usage */}
      {hasUsage || usageSafe ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <UsageCard
            title="Tokens Used"
            value={usageSafe.current_period_tokens?.toLocaleString() || '0'}
            subtitle={
              usageSafe.monthly_token_limit 
                ? `of ${usageSafe.monthly_token_limit.toLocaleString()} (${((usageSafe.current_period_tokens / usageSafe.monthly_token_limit) * 100).toFixed(1)}%)`
                : 'unlimited'
            }
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
      ) : (
        <div className="empty-state-card">
          <div className="empty-state-icon">
            <span className="text-2xl">💰</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Usage Data Yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Start making API requests to see your usage and billing information here.
          </p>
          <button className="btn-primary">
            Create Your First API Key
          </button>
        </div>
      )}

      {/* Billing Cycle Toggle */}
      <div className="flex justify-center">
        <div className="clean-card p-1 flex rounded-2xl">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
              billingCycle === 'monthly'
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
              billingCycle === 'yearly'
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Yearly
            <span className="ml-2 text-green-600 text-xs font-bold bg-green-100 px-2 py-1 rounded-full">
              Save 20%
            </span>
          </button>
        </div>
      </div>

      {/* Freemium Model Access Section */}
      <div className="clean-card p-8 bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <BoltIcon className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Experience Our LLM Gateway</h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Start with our free tier to explore the power of our LLM Gateway. Access free models and upgrade when you're ready for premium features.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="text-left p-6 bg-white rounded-xl shadow-sm">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Free Tier Models</h4>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                  HuggingFace models (free)
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                  Ollama local models
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                  Basic analytics
                </li>
              </ul>
            </div>
            
            <div className="text-left p-6 bg-white rounded-xl shadow-sm">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Premium Models</h4>
              <ul className="space-y-2">
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-blue-500 mr-2" />
                  OpenAI GPT models
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-blue-500 mr-2" />
                  Anthropic Claude models
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-blue-500 mr-2" />
                  Google Gemini models
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <CheckIcon className="h-4 w-4 text-blue-500 mr-2" />
                  And 20+ more providers
                </li>
              </ul>
            </div>
          </div>
          
          <button className="btn-primary">
            Start with Free Tier
          </button>
        </div>
      </div>

      {/* Pricing Plans */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {plans.map((plan) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            isCurrentPlan={plan.id === currentPlan}
          />
        ))}
      </div>

      {/* Usage Breakdown */}
      {hasUsage && usageSafe?.top_models && usageSafe.top_models.length > 0 && (
        <div className="clean-card overflow-hidden">
          <div className="px-6 py-4 table-header">
            <h3 className="text-lg font-semibold text-gray-900">Model Usage Breakdown</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {usageSafe.top_models.map((model, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mr-4" />
                    <span className="text-sm font-medium text-gray-900">{model.model_id}</span>
                  </div>
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

      {/* Invoice History */}
      {invoicesSafe.length > 0 ? (
        <div className="clean-card overflow-hidden">
          <div className="px-6 py-4 table-header">
            <h3 className="text-lg font-semibold text-gray-900">Invoice History</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {invoicesSafe.map((invoice) => (
                  <tr key={invoice.id} className="table-row">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {invoice.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(invoice.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(invoice.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="badge-success">
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button className="text-blue-600 hover:text-blue-800 font-medium">
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="clean-card text-center p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Invoices Yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Your invoice history will appear here once you have billing activity.
          </p>
          <button className="btn-secondary">
            Learn About Billing
          </button>
        </div>
      )}

      {/* Billing Features */}
      <div className="clean-card p-8 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CreditCardIcon className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Transparent, Usage-Based Pricing</h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Pay only for what you use with our transparent pricing model. No hidden fees, no surprises. 
            Scale up or down as needed with real-time usage tracking.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            <div className="flex items-start">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3 mt-1">
                <CheckIcon className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Real-time Tracking</h4>
                <p className="text-sm text-gray-600">Monitor your usage and costs in real-time</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3 mt-1">
                <BoltIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Flexible Limits</h4>
                <p className="text-sm text-gray-600">Set custom limits and alerts for your team</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3 mt-1">
                <CreditCardIcon className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Secure Payments</h4>
                <p className="text-sm text-gray-600">Enterprise-grade security with Stripe</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Billing;