import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const ABTesting = () => {
    const { user } = useAuth();
    const [tests, setTests] = useState([]);
    const [selectedTest, setSelectedTest] = useState(null);
    const [testResults, setTestResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newTest, setNewTest] = useState({
        name: '',
        description: '',
        test_type: 'model_comparison',
        variants: [
            { name: 'A', config: {} },
            { name: 'B', config: {} }
        ],
        traffic_split: { A: 0.5, B: 0.5 },
        duration_days: 7,
        success_metrics: ['response_time', 'cost', 'quality_score'],
        statistical_significance: 0.05
    });

    useEffect(() => {
        // Disable API call until working auth integration is complete
        // loadTests();
        
        // Set empty state for now
        setTests([]);
        setIsLoading(false);
    }, []);

    const loadTests = async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/api/ab-testing/tests');
            setTests(response.data || []);
        } catch (error) {
            console.error('Failed to load A/B tests:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadTestResults = async (testId) => {
        try {
            setIsLoading(true);
            const response = await api.get(`/api/ab-testing/tests/${testId}/results`);
            setTestResults(response.data);
        } catch (error) {
            console.error('Failed to load test results:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const createTest = async () => {
        try {
            setIsLoading(true);
            const testData = {
                ...newTest,
                variants: newTest.variants.reduce((acc, variant) => {
                    acc[variant.name] = variant.config;
                    return acc;
                }, {})
            };

            await api.post('/api/ab-testing/tests', testData);
            setShowCreateForm(false);
            setNewTest({
                name: '',
                description: '',
                test_type: 'model_comparison',
                variants: [
                    { name: 'A', config: {} },
                    { name: 'B', config: {} }
                ],
                traffic_split: { A: 0.5, B: 0.5 },
                duration_days: 7,
                success_metrics: ['response_time', 'cost', 'quality_score'],
                statistical_significance: 0.05
            });
            loadTests();
        } catch (error) {
            console.error('Failed to create A/B test:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const stopTest = async (testId) => {
        try {
            await api.post(`/api/ab-testing/tests/${testId}/stop`);
            loadTests();
        } catch (error) {
            console.error('Failed to stop A/B test:', error);
        }
    };

    const addVariant = () => {
        const variantName = String.fromCharCode(65 + newTest.variants.length); // A, B, C, etc.
        setNewTest(prev => ({
            ...prev,
            variants: [...prev.variants, { name: variantName, config: {} }]
        }));
    };

    const removeVariant = (index) => {
        setNewTest(prev => ({
            ...prev,
            variants: prev.variants.filter((_, i) => i !== index)
        }));
    };

    const updateVariant = (index, field, value) => {
        setNewTest(prev => ({
            ...prev,
            variants: prev.variants.map((variant, i) => 
                i === index ? { ...variant, [field]: value } : variant
            )
        }));
    };

    const updateTrafficSplit = () => {
        const totalVariants = newTest.variants.length;
        const split = 1 / totalVariants;
        const trafficSplit = {};
        newTest.variants.forEach(variant => {
            trafficSplit[variant.name] = split;
        });
        setNewTest(prev => ({ ...prev, traffic_split: trafficSplit }));
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'active': return 'bg-green-100 text-green-800';
            case 'stopped': return 'bg-red-100 text-red-800';
            case 'completed': return 'bg-blue-100 text-blue-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getTestTypeLabel = (type) => {
        const labels = {
            'model_comparison': 'Model Comparison',
            'provider_comparison': 'Provider Comparison',
            'cost_optimization': 'Cost Optimization',
            'quality_assessment': 'Quality Assessment'
        };
        return labels[type] || type;
    };

    return (
        <>
            <div className="space-y-8">
                {/* Page Header */}
                <div>
                    <h1 className="text-3xl font-bold gradient-text mb-2">A/B Testing</h1>
                    <p className="text-gray-600">
                        Create and manage A/B tests to optimize model performance, costs, and quality.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Panel - Test List */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-semibold">A/B Tests</h2>
                                <button
                                    onClick={() => setShowCreateForm(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Create Test
                                </button>
                            </div>

                            {isLoading ? (
                                <div className="text-center py-4">Loading...</div>
                            ) : (
                                <div className="space-y-3">
                                    {tests.map(test => (
                                        <div
                                            key={test.id}
                                            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                                                selectedTest?.id === test.id
                                                    ? 'border-blue-500 bg-blue-50'
                                                    : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                            onClick={() => {
                                                setSelectedTest(test);
                                                loadTestResults(test.id);
                                            }}
                                        >
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <div className="font-medium text-gray-900">
                                                        {test.name}
                                                    </div>
                                                    <div className="text-sm text-gray-500">
                                                        {getTestTypeLabel(test.test_type)}
                                                    </div>
                                                    <div className="text-xs text-gray-400">
                                                        {new Date(test.created_at).toLocaleDateString()}
                                                    </div>
                                                </div>
                                                <span className={`px-2 py-1 rounded text-xs ${getStatusColor(test.status)}`}>
                                                    {test.status}
                                                </span>
                                            </div>
                                            <div className="mt-2 text-xs text-gray-500">
                                                {test.total_executions} executions • {test.total_results} results
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Panel - Test Details and Results */}
                    <div className="lg:col-span-2 space-y-6">
                        {selectedTest && (
                            <>
                                {/* Test Details */}
                                <div className="bg-white rounded-lg shadow p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h2 className="text-xl font-semibold">{selectedTest.name}</h2>
                                            <p className="text-gray-600">{selectedTest.description}</p>
                                        </div>
                                        {selectedTest.status === 'active' && (
                                            <button
                                                onClick={() => stopTest(selectedTest.id)}
                                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                                            >
                                                Stop Test
                                            </button>
                                        )}
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <div className="text-sm font-medium text-gray-500">Test Type</div>
                                            <div className="text-gray-900">{getTestTypeLabel(selectedTest.test_type)}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-gray-500">Status</div>
                                            <div className="text-gray-900">{selectedTest.status}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-gray-500">Created</div>
                                            <div className="text-gray-900">
                                                {new Date(selectedTest.created_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-gray-500">Expires</div>
                                            <div className="text-gray-900">
                                                {new Date(selectedTest.expires_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Test Results */}
                                {testResults && (
                                    <div className="bg-white rounded-lg shadow p-6">
                                        <h3 className="text-lg font-semibold mb-4">Test Results</h3>
                                        
                                        {testResults.winner && (
                                            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                                                <div className="font-medium text-green-800">Winner: Variant {testResults.winner}</div>
                                            </div>
                                        )}

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {Object.entries(testResults.variant_results || {}).map(([variant, results]) => (
                                                <div key={variant} className="border border-gray-200 rounded-lg p-4">
                                                    <h4 className="font-medium text-gray-900 mb-3">Variant {variant}</h4>
                                                    
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-500">Total Executions:</span>
                                                            <span className="text-sm font-medium">{results.total_executions}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-500">Success Rate:</span>
                                                            <span className="text-sm font-medium">
                                                                {(results.success_rate * 100).toFixed(1)}%
                                                            </span>
                                                        </div>
                                                        
                                                        {results.metrics && Object.entries(results.metrics).map(([metric, data]) => (
                                                            <div key={metric} className="border-t pt-2">
                                                                <div className="text-sm font-medium text-gray-700 mb-1">
                                                                    {metric.replace('_', ' ').toUpperCase()}
                                                                </div>
                                                                <div className="grid grid-cols-2 gap-2 text-xs">
                                                                    <div>Mean: {data.mean?.toFixed(2)}</div>
                                                                    <div>Std Dev: {data.std_dev?.toFixed(2)}</div>
                                                                    <div>Min: {data.min?.toFixed(2)}</div>
                                                                    <div>Max: {data.max?.toFixed(2)}</div>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        {testResults.statistical_analysis && (
                                            <div className="mt-6 border-t pt-4">
                                                <h4 className="font-medium text-gray-900 mb-3">Statistical Analysis</h4>
                                                <div className="space-y-2">
                                                    {Object.entries(testResults.statistical_analysis.significant_differences || {}).map(([comparison, data]) => (
                                                        <div key={comparison} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                            <span className="text-sm font-medium">{comparison}</span>
                                                            <span className={`px-2 py-1 rounded text-xs ${
                                                                data.significant ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                            }`}>
                                                                {data.significant ? 'Significant' : 'Not Significant'}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </>
                        )}

                        {!selectedTest && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <div className="text-center py-8">
                                    <div className="text-gray-500">Select an A/B test to view details and results</div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Create Test Modal */}
                {showCreateForm && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold">Create A/B Test</h2>
                                <button
                                    onClick={() => setShowCreateForm(false)}
                                    className="text-gray-500 hover:text-gray-700"
                                >
                                    ✕
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Test Name
                                    </label>
                                    <input
                                        type="text"
                                        value={newTest.name}
                                        onChange={(e) => setNewTest(prev => ({ ...prev, name: e.target.value }))}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Enter test name"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        value={newTest.description}
                                        onChange={(e) => setNewTest(prev => ({ ...prev, description: e.target.value }))}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Enter test description"
                                        rows={3}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Test Type
                                    </label>
                                    <select
                                        value={newTest.test_type}
                                        onChange={(e) => setNewTest(prev => ({ ...prev, test_type: e.target.value }))}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    >
                                        <option value="model_comparison">Model Comparison</option>
                                        <option value="provider_comparison">Provider Comparison</option>
                                        <option value="cost_optimization">Cost Optimization</option>
                                        <option value="quality_assessment">Quality Assessment</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Duration (days)
                                    </label>
                                    <input
                                        type="number"
                                        value={newTest.duration_days}
                                        onChange={(e) => setNewTest(prev => ({ ...prev, duration_days: parseInt(e.target.value) }))}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        min="1"
                                        max="30"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Variants
                                    </label>
                                    <div className="space-y-3">
                                        {newTest.variants.map((variant, index) => (
                                            <div key={index} className="flex items-center space-x-3">
                                                <input
                                                    type="text"
                                                    value={variant.name}
                                                    onChange={(e) => updateVariant(index, 'name', e.target.value)}
                                                    className="w-20 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="Name"
                                                />
                                                <input
                                                    type="text"
                                                    value={JSON.stringify(variant.config)}
                                                    onChange={(e) => {
                                                        try {
                                                            const config = JSON.parse(e.target.value);
                                                            updateVariant(index, 'config', config);
                                                        } catch (error) {
                                                            // Invalid JSON, ignore
                                                        }
                                                    }}
                                                    className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="Config (JSON)"
                                                />
                                                {newTest.variants.length > 2 && (
                                                    <button
                                                        onClick={() => removeVariant(index)}
                                                        className="px-2 py-2 text-red-600 hover:text-red-700"
                                                    >
                                                        ✕
                                                    </button>
                                                )}
                                            </div>
                                        ))}
                                        <button
                                            onClick={addVariant}
                                            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                                        >
                                            Add Variant
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Traffic Split
                                    </label>
                                    <div className="grid grid-cols-2 gap-3">
                                        {newTest.variants.map(variant => (
                                            <div key={variant.name} className="flex items-center space-x-2">
                                                <span className="text-sm font-medium">{variant.name}:</span>
                                                <input
                                                    type="number"
                                                    value={newTest.traffic_split[variant.name] || 0}
                                                    onChange={(e) => setNewTest(prev => ({
                                                        ...prev,
                                                        traffic_split: {
                                                            ...prev.traffic_split,
                                                            [variant.name]: parseFloat(e.target.value)
                                                        }
                                                    }))}
                                                    className="w-20 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    step="0.1"
                                                    min="0"
                                                    max="1"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                    <button
                                        onClick={updateTrafficSplit}
                                        className="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                    >
                                        Equal Split
                                    </button>
                                </div>

                                <div className="flex justify-end space-x-3 pt-4">
                                    <button
                                        onClick={() => setShowCreateForm(false)}
                                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={createTest}
                                        disabled={isLoading || !newTest.name}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isLoading ? 'Creating...' : 'Create Test'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default ABTesting; 