import React, { useState } from 'react';
import { 
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  CpuChipIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Pricing = () => {
  const [billingCycle, setBillingCycle] = useState('monthly');

  const pricingTiers = {
    basic: {
      name: 'Basic',
      price: { monthly: 'Custom', yearly: 'Custom' },
      description: 'Perfect for smaller teams and startups',
      features: [
        { text: '50,000 tokens per month', included: true },
        { text: 'Core models (OpenAI, Anthropic, Google)', included: true },
        { text: 'API keys', included: true },
        { text: 'Basic analytics', included: true },
        { text: 'Email support', included: true },
        { text: '20% platform fee', included: true },
        { text: 'Advanced routing', included: false },
        { text: 'Team management', included: false },
        { text: 'Custom integrations', included: false },
        { text: 'White-label options', included: false },
        { text: 'Dedicated support', included: false },
        { text: 'SLA guarantee', included: false }
      ],
      cta: 'Contact Sales',
      popular: false
    },
    pro: {
      name: 'Pro',
      price: { monthly: 'Custom', yearly: 'Custom' },
      description: 'For mid-market teams and growing companies',
      features: [
        { text: '500,000 tokens per month', included: true },
        { text: 'All models (50+ providers)', included: true },
        { text: 'Advanced routing & load balancing', included: true },
        { text: 'Team management (up to 10 users)', included: true },
        { text: 'Advanced analytics & insights', included: true },
        { text: 'Priority support', included: true },
        { text: '15% platform fee', included: true },
        { text: 'Custom integrations', included: false },
        { text: 'White-label options', included: false },
        { text: 'Dedicated support', included: false },
        { text: 'SLA guarantee', included: false },
        { text: 'On-premise deployment', included: false }
      ],
      cta: 'Contact Sales',
      popular: true
    },
    enterprise: {
      name: 'Enterprise',
      price: { monthly: 'Custom', yearly: 'Custom' },
      description: 'For large organizations with custom needs',
      features: [
        { text: 'Unlimited tokens', included: true },
        { text: 'All models (50+ providers)', included: true },
        { text: 'Advanced routing & load balancing', included: true },
        { text: 'Unlimited team management', included: true },
        { text: 'Custom integrations', included: true },
        { text: 'White-label options', included: true },
        { text: 'Dedicated support', included: true },
        { text: 'SLA guarantee', included: true },
        { text: '10% platform fee', included: true },
        { text: 'Custom billing', included: true },
        { text: 'On-premise deployment', included: true },
        { text: 'Security audit & compliance', included: true }
      ],
      cta: 'Contact Sales',
      popular: false
    }
  };

  const getPrice = (tier) => {
    const price = tier.price[billingCycle];
    if (price === 0) return 'Free';
    if (price === 'Custom') return 'Custom';
    const discount = billingCycle === 'yearly' ? 0.17 : 0; // 17% discount for yearly
    const finalPrice = price * (1 - discount);
    return `$${finalPrice}${billingCycle === 'yearly' ? '/mo' : '/mo'}`;
  };

  const getSavings = (tier) => {
    if (tier.price[billingCycle] === 'Custom' || tier.price[billingCycle] === 0) return null;
    if (billingCycle === 'yearly') {
      return `Save ${Math.round((1 - (tier.price.yearly / (tier.price.monthly * 12))) * 100)}%`;
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Choose the plan that fits your needs. All plans include our unified API and intelligent routing.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                billingCycle === 'yearly' ? 'bg-[#000000]' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Yearly
              <span className="ml-1 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                Save 17%
              </span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {Object.entries(pricingTiers).map(([tierKey, tier]) => (
            <div
              key={tierKey}
              className={`relative bg-white rounded-2xl shadow-lg border-2 transition-all duration-300 hover:shadow-xl ${
                tier.popular
                  ? 'border-[#000000] scale-105'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-[#000000] text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="p-8">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
                  <p className="text-gray-600 mb-4">{tier.description}</p>
                  <div className="mb-2">
                    <span className="text-4xl font-bold text-[#000000]">{getPrice(tier)}</span>
                  </div>
                  {getSavings(tier) && (
                    <span className="text-sm text-green-600 font-medium">{getSavings(tier)}</span>
                  )}
                </div>

                <div className="space-y-4 mb-8">
                  {tier.features.map((feature, index) => (
                    <div key={index} className="flex items-start">
                      {feature.included ? (
                        <CheckIcon className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                      ) : (
                        <XMarkIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-3 flex-shrink-0" />
                      )}
                      <span className={`text-sm ${feature.included ? 'text-gray-900' : 'text-gray-500'}`}>
                        {feature.text}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105 ${
                    tier.popular
                      ? 'bg-[#000000] hover:bg-[#14213d] text-white shadow-lg'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  {tier.cta}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Platform Fees */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <CpuChipIcon className="h-6 w-6 text-[#000000] mr-2" />
              Platform Fees
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Basic Tier</span>
                <span className="font-semibold">20% markup</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Pro Tier</span>
                <span className="font-semibold">15% markup</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Enterprise</span>
                <span className="font-semibold">10% markup</span>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              Platform fees are added to provider costs to cover infrastructure, support, and development.
            </p>
          </div>

          {/* Value Proposition */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <SparklesIcon className="h-6 w-6 text-[#000000] mr-2" />
              What You Get
            </h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm text-gray-700">Unified API for 50+ providers</span>
              </div>
              <div className="flex items-center">
                <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm text-gray-700">Intelligent model routing</span>
              </div>
              <div className="flex items-center">
                <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm text-gray-700">Usage analytics & monitoring</span>
              </div>
              <div className="flex items-center">
                <CheckIcon className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm text-gray-700">Reliable infrastructure</span>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-12">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">How do platform fees work?</h3>
              <p className="text-gray-600 text-sm">
                Platform fees are a percentage markup added to provider costs. This covers our infrastructure, 
                support, and ongoing development costs.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">Can I switch plans anytime?</h3>
              <p className="text-gray-600 text-sm">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately 
                and are prorated for the current billing period.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">What happens if I exceed my token limit?</h3>
              <p className="text-gray-600 text-sm">
                For Basic and Pro plans, you'll be notified when approaching your limit. You can upgrade 
                or contact our sales team to discuss options. Enterprise plans have unlimited usage.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">Do you offer refunds?</h3>
              <p className="text-gray-600 text-sm">
                We offer a 30-day money-back guarantee for all plans. If you're not satisfied, 
                contact our support team for a full refund.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;