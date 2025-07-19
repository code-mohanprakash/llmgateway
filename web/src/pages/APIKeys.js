import React, { useState, useEffect } from 'react';
import { PlusIcon, EyeIcon, EyeSlashIcon, TrashIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';

const APIKeys = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');

  useEffect(() => {
    // Disable API call until working auth integration is complete
    // fetchApiKeys();
    
    // Set empty state for now
    setApiKeys([]);
    setLoading(false);
  }, []);

  const fetchApiKeys = async () => {
    try {
      setLoading(true);
      const response = await api.get('/auth/api-keys');
      setApiKeys(response.data.map(key => ({
        ...key,
        isVisible: false
      })));
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
      toast.error(message || 'Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const toggleKeyVisibility = (keyId) => {
    setApiKeys(keys => keys.map(key => 
      key.id === keyId ? { ...key, isVisible: !key.isVisible } : key
    ));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('API key copied to clipboard!');
  };

  const createApiKey = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a name for the API key');
      return;
    }

    try {
      const response = await api.post('/auth/api-keys', {
        name: newKeyName
      });
      
      const newKey = {
        ...response.data,
        isVisible: true
      };

      setApiKeys([newKey, ...apiKeys]);
      setNewKeyName('');
      setShowCreateModal(false);
      toast.success('API key created successfully!');
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
      toast.error(message || 'Failed to create API key');
    }
  };

  const deleteApiKey = async (keyId) => {
    if (window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      try {
        await api.delete(`/auth/api-keys/${keyId}`);
        setApiKeys(keys => keys.filter(key => key.id !== keyId));
        toast.success('API key deleted successfully');
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
        toast.error(message || 'Failed to delete API key');
      }
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">API Keys</h1>
            <p className="text-gray-600 mt-1">Manage your API keys for accessing the Model Bridge</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-gray-900 to-black hover:from-black hover:to-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create API Key
          </button>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-gray-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600 mt-1">Manage your API keys for accessing the Model Bridge</p>
        </div>
                  <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-gray-900 to-black hover:from-black hover:to-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create API Key
          </button>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-800 mb-2">API Key Guidelines</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Keep your API keys secure and never share them publicly</li>
          <li>• Use different keys for different environments (development, staging, production)</li>
          <li>• Regularly rotate your API keys for enhanced security</li>
          <li>• Monitor usage to detect any unauthorized access</li>
          <li>• <strong>Note:</strong> API keys are only shown once when created for security</li>
        </ul>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Your API Keys</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {apiKeys.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-gray-500 text-lg">🔑</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">No API Keys Yet</h3>
              <p className="text-gray-500 max-w-sm mx-auto mb-4">
                Create your first API key to start making requests to the Model Bridge.
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-gray-900 to-black hover:from-black hover:to-gray-900 transition-all duration-200"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create your first API key
              </button>
            </div>
          ) : (
            apiKeys.map((apiKey) => (
              <div key={apiKey.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-sm font-medium text-gray-900">{apiKey.name}</h4>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    </div>
                    <div className="mt-2">
                      <div className="flex items-center space-x-2">
                        <code className="text-sm bg-gray-100 px-2 py-1 rounded font-mono">
                          {apiKey.isVisible ? (apiKey.api_key || 'No key available') : (apiKey.api_key ? `${apiKey.api_key.substring(0, 8)}...${apiKey.api_key.substring(apiKey.api_key.length - 4)}` : 'llm_...key')}
                        </code>
                        <button
                          onClick={() => toggleKeyVisibility(apiKey.id)}
                          className="text-gray-400 hover:text-gray-600"
                          title={apiKey.api_key ? "Toggle visibility" : "API key not available"}
                        >
                          {apiKey.isVisible ? (
                            <EyeSlashIcon className="h-4 w-4" />
                          ) : (
                            <EyeIcon className="h-4 w-4" />
                          )}
                        </button>
                        {apiKey.isVisible && apiKey.api_key && (
                          <button
                            onClick={() => copyToClipboard(apiKey.api_key)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <DocumentDuplicateIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500 space-y-1">
                      <p>Created: {formatDate(apiKey.created_at)}</p>
                      <p>Last used: {formatDate(apiKey.last_used_at)}</p>
                      <p>Total requests: {apiKey.request_count?.toLocaleString() || '0'}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => deleteApiKey(apiKey.id)}
                      className="text-red-400 hover:text-red-600"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Create New API Key</h3>
            </div>
            <div className="px-6 py-4">
              <label htmlFor="keyName" className="block text-sm font-medium text-gray-700 mb-2">
                API Key Name
              </label>
              <input
                id="keyName"
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Production API Key"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
              />
              <p className="mt-2 text-sm text-gray-500">
                Choose a descriptive name to help you identify this key later.
              </p>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setNewKeyName('');
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={createApiKey}
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-gray-900 to-black rounded-md hover:from-black hover:to-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
              >
                Create Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIKeys;