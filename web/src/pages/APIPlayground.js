import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const APIPlayground = () => {
    const { user } = useAuth();
    const [selectedEndpoint, setSelectedEndpoint] = useState('chat');
    const [requestData, setRequestData] = useState('');
    const [responseData, setResponseData] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [generatedCode, setGeneratedCode] = useState('');
    const [selectedLanguage, setSelectedLanguage] = useState('python');
    const [authToken, setAuthToken] = useState('');
    const [endpointHistory, setEndpointHistory] = useState([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const streamRef = useRef(null);

    const endpoints = [
        {
            name: 'Chat Completion',
            value: 'chat',
            method: 'POST',
            path: '/api/llm/chat',
            description: 'Send chat completion request to any supported model',
            defaultData: {
                messages: [
                    { role: 'user', content: 'Hello, how are you?' }
                ],
                model: 'gpt-3.5-turbo',
                temperature: 0.7
            }
        },
        {
            name: 'Text Completion',
            value: 'completion',
            method: 'POST',
            path: '/api/llm/completion',
            description: 'Send text completion request to any supported model',
            defaultData: {
                prompt: 'Write a short story about a robot.',
                model: 'gpt-3.5-turbo',
                temperature: 0.7
            }
        },
        {
            name: 'Get Models',
            value: 'models',
            method: 'GET',
            path: '/api/llm/models',
            description: 'Get list of available models',
            defaultData: {}
        },
        {
            name: 'Get Providers',
            value: 'providers',
            method: 'GET',
            path: '/api/llm/providers',
            description: 'Get list of available providers',
            defaultData: {}
        },
        {
            name: 'Create Workflow',
            value: 'workflow',
            method: 'POST',
            path: '/api/workflows',
            description: 'Create a new workflow',
            defaultData: {
                name: 'My Workflow',
                description: 'A sample workflow',
                definition: {
                    steps: [
                        {
                            id: 'step1',
                            type: 'llm',
                            config: {
                                model: 'gpt-3.5-turbo',
                                prompt: '{{input}}'
                            }
                        }
                    ]
                }
            }
        },
        {
            name: 'Execute Workflow',
            value: 'execute',
            method: 'POST',
            path: '/api/workflows/execute',
            description: 'Execute a workflow',
            defaultData: {
                workflow_id: 'workflow-id',
                input_data: {
                    input: 'Hello world'
                }
            }
        },
        {
            name: 'Get Usage Analytics',
            value: 'analytics',
            method: 'GET',
            path: '/api/analytics/usage',
            description: 'Get usage analytics',
            defaultData: {}
        },
        {
            name: 'Get Audit Logs',
            value: 'audit',
            method: 'GET',
            path: '/api/audit/logs',
            description: 'Get audit logs',
            defaultData: {}
        }
    ];

    useEffect(() => {
        if (user?.token) {
            setAuthToken(user.token);
        }
    }, [user]);

    useEffect(() => {
        const endpoint = endpoints.find(ep => ep.value === selectedEndpoint);
        if (endpoint) {
            setRequestData(JSON.stringify(endpoint.defaultData, null, 2));
        }
    }, [selectedEndpoint]);

    const handleEndpointChange = (endpoint) => {
        setSelectedEndpoint(endpoint);
        setResponseData('');
        setError('');
        setGeneratedCode('');
    };

    const handleSendRequest = async () => {
        setIsLoading(true);
        setError('');
        setResponseData('');

        try {
            const endpoint = endpoints.find(ep => ep.value === selectedEndpoint);
            const data = requestData ? JSON.parse(requestData) : {};

            let response;
            if (endpoint.method === 'GET') {
                const params = new URLSearchParams(data).toString();
                const url = params ? `${endpoint.path}?${params}` : endpoint.path;
                response = await api.get(url);
            } else {
                response = await api.post(endpoint.path, data);
            }

            setResponseData(JSON.stringify(response, null, 2));
            generateCode(endpoint, data, response);
            addToHistory(endpoint, data, response);

        } catch (err) {
            setError(err.message || 'Request failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleStreamRequest = async () => {
        setIsStreaming(true);
        setError('');
        setResponseData('');

        try {
            const endpoint = endpoints.find(ep => ep.value === selectedEndpoint);
            const data = requestData ? JSON.parse(requestData) : {};

            // Add streaming flag
            data.stream = true;

            const response = await fetch(`${process.env.REACT_APP_API_URL}${endpoint.path}`, {
                method: endpoint.method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            setIsStreaming(false);
                            return;
                        }
                        try {
                            const parsed = JSON.parse(data);
                            setResponseData(prev => prev + JSON.stringify(parsed, null, 2) + '\n');
                        } catch (e) {
                            // Ignore parsing errors for streaming
                        }
                    }
                }
            }

        } catch (err) {
            setError(err.message || 'Streaming request failed');
        } finally {
            setIsStreaming(false);
        }
    };

    const generateCode = (endpoint, requestData, responseData) => {
        let code = '';

        switch (selectedLanguage) {
            case 'python':
                code = generatePythonCode(endpoint, requestData, responseData);
                break;
            case 'javascript':
                code = generateJavaScriptCode(endpoint, requestData, responseData);
                break;
            case 'curl':
                code = generateCurlCode(endpoint, requestData);
                break;
            default:
                code = generatePythonCode(endpoint, requestData, responseData);
        }

        setGeneratedCode(code);
    };

    const generatePythonCode = (endpoint, requestData, responseData) => {
        const dataStr = JSON.stringify(requestData, null, 4);
        return `import requests
import json

url = "${process.env.REACT_APP_API_URL}${endpoint.path}"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = ${dataStr}

response = requests.${endpoint.method.toLowerCase()}(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print("Response:")
print(json.dumps(response.json(), indent=2))`;
    };

    const generateJavaScriptCode = (endpoint, requestData, responseData) => {
        const dataStr = JSON.stringify(requestData, null, 4);
        return `const url = "${process.env.REACT_APP_API_URL}${endpoint.path}";
const headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
};
const data = ${dataStr};

fetch(url, {
    method: "${endpoint.method}",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    console.log("Response:", data);
})
.catch(error => {
    console.error("Error:", error);
});`;
    };

    const generateCurlCode = (endpoint, requestData) => {
        const dataStr = JSON.stringify(requestData);
        return `curl -X ${endpoint.method} \\
  "${process.env.REACT_APP_API_URL}${endpoint.path}" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '${dataStr}'`;
    };

    const addToHistory = (endpoint, requestData, responseData) => {
        const historyItem = {
            id: Date.now(),
            endpoint: endpoint.name,
            method: endpoint.method,
            path: endpoint.path,
            requestData,
            responseData,
            timestamp: new Date().toISOString()
        };

        setEndpointHistory(prev => [historyItem, ...prev.slice(0, 9)]);
    };

    const loadFromHistory = (item) => {
        setRequestData(JSON.stringify(item.requestData, null, 2));
        setResponseData(JSON.stringify(item.responseData, null, 2));
    };

    const clearHistory = () => {
        setEndpointHistory([]);
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <>
            <div className="space-y-8">
                {/* Page Header */}
                <div>
                    <h1 className="text-3xl font-bold gradient-text mb-2">API Playground</h1>
                    <p className="text-gray-600">
                        Test the Model Bridge API endpoints interactively. Build requests, see responses, and generate code examples.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Panel - Endpoint Selection and Request */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Endpoint Selection */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold mb-4">Select Endpoint</h2>
                            <select
                                value={selectedEndpoint}
                                onChange={(e) => handleEndpointChange(e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                {endpoints.map(endpoint => (
                                    <option key={endpoint.value} value={endpoint.value}>
                                        {endpoint.name}
                                    </option>
                                ))}
                            </select>
                            
                            {endpoints.find(ep => ep.value === selectedEndpoint) && (
                                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                                    <h3 className="font-medium text-gray-900 mb-2">
                                        {endpoints.find(ep => ep.value === selectedEndpoint).name}
                                    </h3>
                                    <p className="text-sm text-gray-600 mb-2">
                                        {endpoints.find(ep => ep.value === selectedEndpoint).description}
                                    </p>
                                    <div className="text-xs text-gray-500">
                                        <span className="font-medium">Method:</span> {endpoints.find(ep => ep.value === selectedEndpoint).method}
                                        <br />
                                        <span className="font-medium">Path:</span> {endpoints.find(ep => ep.value === selectedEndpoint).path}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Authentication */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold mb-4">Authentication</h2>
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        API Token
                                    </label>
                                    <input
                                        type="password"
                                        value={authToken}
                                        onChange={(e) => setAuthToken(e.target.value)}
                                        placeholder="Enter your API token"
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => setAuthToken(user?.token || '')}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                        Use Current Token
                                    </button>
                                    <button
                                        onClick={() => setAuthToken('')}
                                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Request Controls */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold mb-4">Request</h2>
                            <div className="space-y-3">
                                <button
                                    onClick={handleSendRequest}
                                    disabled={isLoading || !authToken}
                                    className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? 'Sending...' : 'Send Request'}
                                </button>
                                
                                {selectedEndpoint === 'chat' && (
                                    <button
                                        onClick={handleStreamRequest}
                                        disabled={isStreaming || !authToken}
                                        className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isStreaming ? 'Streaming...' : 'Stream Response'}
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Middle Panel - Request/Response */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Request Data */}
                        <div className="bg-white rounded-lg shadow">
                            <div className="p-6 border-b border-gray-200">
                                <h2 className="text-lg font-semibold">Request Data</h2>
                            </div>
                            <div className="p-6">
                                <textarea
                                    value={requestData}
                                    onChange={(e) => setRequestData(e.target.value)}
                                    placeholder="Enter JSON request data..."
                                    className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                        </div>

                        {/* Response Data */}
                        <div className="bg-white rounded-lg shadow">
                            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                                <h2 className="text-lg font-semibold">Response</h2>
                                {responseData && (
                                    <button
                                        onClick={() => copyToClipboard(responseData)}
                                        className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors"
                                    >
                                        Copy
                                    </button>
                                )}
                            </div>
                            <div className="p-6">
                                {error ? (
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                        <div className="text-red-800 font-medium">Error:</div>
                                        <div className="text-red-700 mt-1">{error}</div>
                                    </div>
                                ) : (
                                    <pre className="w-full h-64 p-4 bg-gray-50 border border-gray-300 rounded-lg font-mono text-sm overflow-auto">
                                        {responseData || 'No response yet...'}
                                    </pre>
                                )}
                            </div>
                        </div>

                        {/* Generated Code */}
                        {generatedCode && (
                            <div className="bg-white rounded-lg shadow">
                                <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                                    <div className="flex items-center space-x-4">
                                        <h2 className="text-lg font-semibold">Generated Code</h2>
                                        <select
                                            value={selectedLanguage}
                                            onChange={(e) => setSelectedLanguage(e.target.value)}
                                            className="px-3 py-1 border border-gray-300 rounded text-sm"
                                        >
                                            <option value="python">Python</option>
                                            <option value="javascript">JavaScript</option>
                                            <option value="curl">cURL</option>
                                        </select>
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(generatedCode)}
                                        className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors"
                                    >
                                        Copy
                                    </button>
                                </div>
                                <div className="p-6">
                                    <pre className="w-full h-48 p-4 bg-gray-50 border border-gray-300 rounded-lg font-mono text-sm overflow-auto">
                                        {generatedCode}
                                    </pre>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* History Section */}
                {endpointHistory.length > 0 && (
                    <div className="mt-8 bg-white rounded-lg shadow">
                        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                            <h2 className="text-lg font-semibold">Request History</h2>
                            <button
                                onClick={clearHistory}
                                className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors"
                            >
                                Clear History
                            </button>
                        </div>
                        <div className="p-6">
                            <div className="space-y-3">
                                {endpointHistory.map(item => (
                                    <div
                                        key={item.id}
                                        className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                        onClick={() => loadFromHistory(item)}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <div className="font-medium text-gray-900">
                                                    {item.endpoint}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {item.method} {item.path}
                                                </div>
                                                <div className="text-xs text-gray-400">
                                                    {new Date(item.timestamp).toLocaleString()}
                                                </div>
                                            </div>
                                            <span className={`px-2 py-1 rounded text-xs ${
                                                item.responseData?.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                                {item.responseData?.success ? 'Success' : 'Error'}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default APIPlayground; 