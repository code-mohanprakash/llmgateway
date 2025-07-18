import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon,
  ClipboardIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';
import api from '../services/api';

const Models = () => {
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    total_models: 0,
    total_providers: 0,
    free_models: 0,
    paid_models: 0
  });

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const response = await api.get('/v1/models/public');
      setModels(response.data.models || {});
      setStats({
        total_models: response.data.total_models || 0,
        total_providers: response.data.total_providers || 0,
        free_models: response.data.free_models || 0,
        paid_models: response.data.paid_models || 0
      });
    } catch (err) {
      // Fallback mock data for testing
      setModels({
        groq: [
          { model_id: 'deepseek-r1-distill-llama-70b', model_name: 'deepseek-r1-distill-llama-70b', context_length: 131072, cost_per_1k_tokens: 0.75, is_free: false },
          { model_id: 'gemma2-9b-it', model_name: 'gemma2-9b-it', context_length: 8192, cost_per_1k_tokens: 0.20, is_free: false },
          { model_id: 'llama-guard-4-12b', model_name: 'llama-guard-4-12b', context_length: 131072, cost_per_1k_tokens: 0.20, is_free: false }
        ],
        'inference.net': [
          { model_id: 'llama-3.1-8b-instruct', model_name: 'llama-3.1-8b-instruct', context_length: 128000, cost_per_1k_tokens: 0.07, is_free: false },
          { model_id: 'llama-3.2-11b-instruct', model_name: 'llama-3.2-11b-instruct', context_length: 128000, cost_per_1k_tokens: 0.07, is_free: false }
        ],
        'kluster.ai': [
          { model_id: 'llama-3.1-8b-instruct', model_name: 'llama-3.1-8b-instruct', context_length: 8192, cost_per_1k_tokens: 0.07, is_free: false }
        ],
        ollama: [
          { model_id: 'llama2', model_name: 'Llama 2', context_length: 4096, cost_per_1k_tokens: 0, is_free: true },
          { model_id: 'mistral', model_name: 'Mistral', context_length: 8192, cost_per_1k_tokens: 0, is_free: true }
        ]
      });
      setStats({
        total_models: 80,
        total_providers: 10,
        free_models: 12,
        paid_models: 68
      });
    } finally {
      setLoading(false);
    }
  };

  const getProviderIcon = (provider) => {
    const icons = {
      groq: `${process.env.PUBLIC_URL}/images/icons8-grok-48.png`,
      'inference.net': `${process.env.PUBLIC_URL}/images/meta-color.png`,
      'kluster.ai': `${process.env.PUBLIC_URL}/images/meta-color.png`,
      openai: `${process.env.PUBLIC_URL}/images/openaiiconq.png`,
      anthropic: `${process.env.PUBLIC_URL}/images/icons8-anthropic-48.png`,
      google: `${process.env.PUBLIC_URL}/images/google-color.png`,
      together: `${process.env.PUBLIC_URL}/images/meta-color.png`,
      mistral: `${process.env.PUBLIC_URL}/images/mistral-color.png`,
      cohere: `${process.env.PUBLIC_URL}/images/cohere-color.png`,
      perplexity: `${process.env.PUBLIC_URL}/images/deepseek-color.png`,
      ollama: `${process.env.PUBLIC_URL}/images/ollama.png`,
      huggingface: `${process.env.PUBLIC_URL}/images/meta-color.png`,
      deepseek: `${process.env.PUBLIC_URL}/images/deepseek-color.png`
    };
    return icons[provider] || `${process.env.PUBLIC_URL}/images/openai.png`;
  };

  const formatCost = (cost, isFree = false) => {
    if (isFree) return 'Free';
    if (cost === 0) return 'Free';
    if (cost < 0.001) return '< $0.001';
    return `$${cost.toFixed(2)}`;
  };

  const formatContextLength = (length) => {
    if (length >= 1000000) return `${(length / 1000000).toFixed(1)}M`;
    if (length >= 1000) return `${(length / 1000).toFixed(1)}k`;
    return length.toString();
  };

  const copyModelId = (modelId) => {
    navigator.clipboard.writeText(modelId);
  };

  const handleTryModel = (model, isFree) => {
    if (isFree) {
      // Redirect to register page for free models
      window.location.href = '/register';
    } else {
      // Redirect to pricing page for paid models
      window.location.href = '/pricing';
    }
  };

  const getFilteredProviders = () => {
    let providers = Object.keys(models);
    if (searchTerm) {
      providers = providers.filter(provider => 
        provider.toLowerCase().includes(searchTerm.toLowerCase()) ||
        models[provider].some(model => 
          model.model_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          model.model_id?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
    return providers;
  };

  const getSortedModels = (providerModels) => {
    return [...providerModels];
  };

  const filteredProviders = getFilteredProviders();

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Navigation />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-[#000000]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
              Supported AI Providers & Models
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Access {stats.total_models} models from {stats.total_providers} leading AI providers through our unified API
            </p>
          </div>

          {/* Search */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search models or providers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#000000] focus:border-transparent transition-all duration-200 bg-white"
              />
            </div>
          </div>

          {/* Providers List */}
          <div className="space-y-12">
            {filteredProviders.map((provider) => {
              const providerModels = getSortedModels(models[provider]);
              const modelCount = providerModels.length;

              return (
                <div key={provider} className="space-y-6">
                  {/* Provider Header */}
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200 shadow-sm">
                      <img 
                        src={getProviderIcon(provider)} 
                        alt={`${provider} logo`}
                        className="w-6 h-6 object-contain"
                        onError={(e) => {
                          console.log(`Failed to load icon for ${provider}:`, getProviderIcon(provider));
                          e.target.style.display = 'none';
                          // Show fallback text
                          const fallback = document.createElement('div');
                          fallback.textContent = provider.charAt(0).toUpperCase();
                          fallback.className = 'text-gray-600 font-bold text-lg';
                          e.target.parentNode.appendChild(fallback);
                        }}
                      />
                    </div>
                    <div className="flex items-center space-x-3">
                      <h2 className="text-2xl font-bold text-gray-900 capitalize">
                        {provider}
                      </h2>
                      <span className="text-gray-500 text-lg">
                        {modelCount} model{modelCount !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>

                  {/* Models Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {providerModels.map((model) => {
                      const isFree = model.is_free;
                      
                      return (
                        <div 
                          key={model.model_id} 
                          className="group border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 relative overflow-hidden bg-white"
                        >
                          {/* Copy Button */}
                          <button
                            onClick={() => copyModelId(model.model_id)}
                            className="absolute top-3 right-3 p-1 text-gray-400 hover:text-[#000000] transition-colors"
                          >
                            <ClipboardIcon className="h-4 w-4" />
                          </button>

                          {/* Try Button - Top Right */}
                          <button
                            onClick={() => handleTryModel(model, isFree)}
                            className={`absolute top-3 right-12 inline-flex items-center justify-center px-2 py-1 text-xs font-medium rounded-full transition-all duration-300 ease-out transform hover:scale-105 hover:shadow-sm ${
                              isFree 
                                ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 border border-green-200/50 hover:from-green-100 hover:to-emerald-100 hover:border-green-300/50' 
                                : 'bg-gradient-to-r from-gray-50 to-slate-50 text-gray-700 border border-gray-200/50 hover:from-gray-100 hover:to-slate-100 hover:border-gray-300/50'
                            }`}
                          >
                            <span className="relative">
                              {isFree ? 'Try for Free' : 'Try'}
                              <div className={`absolute inset-0 rounded-full opacity-0 transition-opacity duration-300 ${
                                isFree ? 'bg-green-200/20' : 'bg-gray-200/20'
                              }`}></div>
                            </span>
                          </button>

                          <div className="space-y-3">
                            {/* Model Name */}
                            <h3 className="font-semibold text-gray-900 text-sm truncate">
                              {model.model_name || model.model_id}
                            </h3>
                            
                            {/* Provider Name */}
                            <p className="text-xs text-gray-500 capitalize">
                              {provider}
                            </p>

                            {/* Model Details */}
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-600">Context:</span>
                                <span className="font-semibold text-gray-900 text-sm">
                                  {formatContextLength(model.context_length)}
                                </span>
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-600">Cost:</span>
                                <span className="font-semibold text-gray-900 text-sm">
                                  {formatCost(model.cost_per_1k_tokens, model.is_free)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* No Results */}
          {filteredProviders.length === 0 && (
            <div className="text-center py-16">
              <div className="text-gray-500 text-xl mb-4">No providers found</div>
              <div className="text-gray-400 text-sm">Try adjusting your search</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Models;