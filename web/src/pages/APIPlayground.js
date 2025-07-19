import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const APIPlayground = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('playground'); // 'playground' or 'documentation'
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
    
    // Documentation state
    const [documentationData, setDocumentationData] = useState({});
    const [availableEndpoints, setAvailableEndpoints] = useState([]);
    const [selectedDocEndpoint, setSelectedDocEndpoint] = useState('');
    const [enterpriseGuides, setEnterpriseGuides] = useState([]);
    const [bestPractices, setBestPractices] = useState([]);
    const [isLoadingDocs, setIsLoadingDocs] = useState(false);

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

    // Load documentation data
    useEffect(() => {
        if (activeTab === 'documentation') {
            loadDocumentation();
        }
    }, [activeTab]);

    const loadDocumentation = async () => {
        setIsLoadingDocs(true);
        try {
            // Load all documentation data
            const [endpointsRes, guidesRes, practicesRes] = await Promise.all([
                api.get('/api/documentation/endpoints'),
                api.get('/api/documentation/enterprise-guides'),
                api.get('/api/documentation/best-practices')
            ]);
            
            setDocumentationData(endpointsRes);
            setAvailableEndpoints(Object.keys(endpointsRes));
            setEnterpriseGuides(guidesRes);
            setBestPractices(practicesRes);
            
            if (Object.keys(endpointsRes).length > 0) {
                setSelectedDocEndpoint(Object.keys(endpointsRes)[0]);
            }
        } catch (err) {
            console.error('Error loading documentation:', err);
        } finally {
            setIsLoadingDocs(false);
        }
    };

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

    const generateCodeFromBackend = async (endpoint, method, language) => {
        try {
            const response = await api.get(`/api/playground/code-sample?endpoint=${endpoint}&method=${method}&language=${language}`);
            setGeneratedCode(response);
        } catch (err) {
            console.error('Error generating code from backend:', err);
            // Fallback to local generation
            generateCode(endpoints.find(ep => ep.path === endpoint), {}, {});
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
                            setResponseData(prev => prev + parsed.choices?.[0]?.delta?.content || '');
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
        switch (selectedLanguage) {
            case 'python':
                setGeneratedCode(generatePythonCode(endpoint, requestData, responseData));
                break;
            case 'javascript':
                setGeneratedCode(generateJavaScriptCode(endpoint, requestData, responseData));
                break;
            case 'curl':
                setGeneratedCode(generateCurlCode(endpoint, requestData));
                break;
            default:
                setGeneratedCode(generatePythonCode(endpoint, requestData, responseData));
        }
    };

    const generatePythonCode = (endpoint, requestData, responseData) => {
        return `import requests
import json

url = "${process.env.REACT_APP_API_URL}${endpoint.path}"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
data = ${JSON.stringify(requestData, null, 4)}

response = requests.${endpoint.method.toLowerCase()}(url, headers=headers, json=data)
print(response.status_code)
print(json.dumps(response.json(), indent=2))`;
    };

    const generateJavaScriptCode = (endpoint, requestData, responseData) => {
        return `const response = await fetch("${process.env.REACT_APP_API_URL}${endpoint.path}", {
    method: "${endpoint.method}",
    headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    },
    body: JSON.stringify(${JSON.stringify(requestData, null, 4)})
});

const data = await response.json();
console.log(data);`;
    };

    const generateCurlCode = (endpoint, requestData) => {
        const data = JSON.stringify(requestData);
        return `curl -X ${endpoint.method} \\
  "${process.env.REACT_APP_API_URL}${endpoint.path}" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '${data}'`;
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
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">API Playground</h1>
                    <p className="text-gray-600">Test and explore the Model Bridge API</p>
                </div>

                {/* Tab Navigation */}
                <div className="mb-6">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            <button
                                onClick={() => setActiveTab('playground')}
                                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                                    activeTab === 'playground'
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                            >
                                API Playground
                            </button>
                            <button
                                onClick={() => setActiveTab('documentation')}
                                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                                    activeTab === 'documentation'
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                            >
                                Documentation
                            </button>
                        </nav>
                    </div>
                </div>

                {activeTab === 'playground' ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Left Column - Request */}
                        <div className="space-y-6">
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">Request</h2>
                                
                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Endpoint
                                    </label>
                                    <select
                                        value={selectedEndpoint}
                                        onChange={(e) => handleEndpointChange(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        {endpoints.map((endpoint) => (
                                            <option key={endpoint.value} value={endpoint.value}>
                                                {endpoint.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Request Data (JSON)
                                    </label>
                                    <textarea
                                        value={requestData}
                                        onChange={(e) => setRequestData(e.target.value)}
                                        rows={8}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                        placeholder="Enter JSON request data..."
                                    />
                                </div>

                                <div className="flex space-x-3">
                                    <button
                                        onClick={handleSendRequest}
                                        disabled={isLoading}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        {isLoading ? 'Sending...' : 'Send Request'}
                                    </button>
                                    <button
                                        onClick={handleStreamRequest}
                                        disabled={isStreaming}
                                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                                    >
                                        {isStreaming ? 'Streaming...' : 'Stream Request'}
                                    </button>
                                </div>
                            </div>

                            {/* History */}
                            {endpointHistory.length > 0 && (
                                <div className="bg-white rounded-lg shadow p-6">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-lg font-semibold text-gray-900">History</h3>
                                        <button
                                            onClick={clearHistory}
                                            className="text-sm text-red-600 hover:text-red-700"
                                        >
                                            Clear
                                        </button>
                                    </div>
                                    <div className="space-y-2">
                                        {endpointHistory.map((item) => (
                                            <div
                                                key={item.id}
                                                onClick={() => loadFromHistory(item)}
                                                className="p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                                            >
                                                <div className="flex justify-between items-center">
                                                    <span className="font-medium text-sm">{item.endpoint}</span>
                                                    <span className="text-xs text-gray-500">
                                                        {new Date(item.timestamp).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-600 mt-1">
                                                    {item.method} {item.path}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Right Column - Response & Code */}
                        <div className="space-y-6">
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">Response</h2>
                                {error && (
                                    <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                                        {error}
                                    </div>
                                )}
                                <textarea
                                    value={responseData}
                                    readOnly
                                    rows={8}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm"
                                />
                                <button
                                    onClick={() => copyToClipboard(responseData)}
                                    className="mt-2 px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                                >
                                    Copy Response
                                </button>
                            </div>

                            <div className="bg-white rounded-lg shadow p-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h2 className="text-lg font-semibold text-gray-900">Generated Code</h2>
                                    <select
                                        value={selectedLanguage}
                                        onChange={(e) => setSelectedLanguage(e.target.value)}
                                        className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                                    >
                                        <option value="python">Python</option>
                                        <option value="javascript">JavaScript</option>
                                        <option value="curl">cURL</option>
                                    </select>
                                </div>
                                <textarea
                                    value={generatedCode}
                                    readOnly
                                    rows={8}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm"
                                />
                                <button
                                    onClick={() => copyToClipboard(generatedCode)}
                                    className="mt-2 px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                                >
                                    Copy Code
                                </button>
                            </div>
                        </div>
                    </div>
                ) : (
                    /* Documentation Tab */
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Left Column - Endpoints List */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">API Endpoints</h2>
                            {isLoadingDocs ? (
                                <div className="text-gray-500">Loading endpoints...</div>
                            ) : (
                                <div className="space-y-2">
                                    {availableEndpoints.map((endpoint) => (
                                        <button
                                            key={endpoint}
                                            onClick={() => setSelectedDocEndpoint(endpoint)}
                                            className={`w-full text-left p-2 rounded-md text-sm ${
                                                selectedDocEndpoint === endpoint
                                                    ? 'bg-blue-100 text-blue-700'
                                                    : 'hover:bg-gray-50'
                                            }`}
                                        >
                                            {endpoint}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Middle Column - Endpoint Documentation */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Endpoint Details</h2>
                            {selectedDocEndpoint && documentationData[selectedDocEndpoint] ? (
                                <div className="space-y-4">
                                    <h3 className="font-medium text-gray-900">{selectedDocEndpoint}</h3>
                                    <pre className="bg-gray-50 p-3 rounded-md text-sm overflow-x-auto">
                                        {JSON.stringify(documentationData[selectedDocEndpoint], null, 2)}
                                    </pre>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => generateCodeFromBackend(selectedDocEndpoint, 'GET', selectedLanguage)}
                                            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                                        >
                                            Generate Code Sample
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-gray-500">Select an endpoint to view details</div>
                            )}
                        </div>

                        {/* Right Column - Enterprise Guides & Best Practices */}
                        <div className="space-y-6">
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">Enterprise Guides</h2>
                                <div className="space-y-3">
                                    {enterpriseGuides.map((guide, index) => (
                                        <div key={index} className="p-3 border border-gray-200 rounded-md">
                                            <h4 className="font-medium text-gray-900">{guide.title}</h4>
                                            <p className="text-sm text-gray-600 mt-1">{guide.content}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">Best Practices</h2>
                                <ul className="space-y-2">
                                    {bestPractices.map((practice, index) => (
                                        <li key={index} className="text-sm text-gray-700 flex items-start">
                                            <span className="text-blue-500 mr-2">•</span>
                                            {practice}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default APIPlayground; 