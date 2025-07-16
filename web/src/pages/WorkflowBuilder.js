import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const WorkflowBuilder = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('builder');
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Workflow builder state
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [steps, setSteps] = useState([]);
  const [selectedStep, setSelectedStep] = useState(null);
  const [showStepModal, setShowStepModal] = useState(false);
  
  // Execution state
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [executionInput, setExecutionInput] = useState('');
  const [executionVariables, setExecutionVariables] = useState('');

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/workflow/workflows');
      setWorkflows(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const loadExecutions = async (workflowId) => {
    try {
      const response = await api.get(`/workflow/workflows/${workflowId}/executions`);
      setExecutions(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load executions');
    }
  };

  const handleCreateWorkflow = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        definition: {
          name: workflowName,
          description: workflowDescription,
          steps: steps,
          variables: {},
          settings: {}
        }
      };
      
      const response = await api.post('/workflow/workflows', workflowData);
      setWorkflows([...workflows, response.data]);
      setWorkflowName('');
      setWorkflowDescription('');
      setSteps([]);
      setActiveTab('workflows');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create workflow');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteWorkflow = async (workflowId) => {
    setLoading(true);
    setError(null);
    
    try {
      let inputData = {};
      let variables = {};
      
      if (executionInput) {
        try {
          inputData = JSON.parse(executionInput);
        } catch (e) {
          throw new Error('Invalid JSON in input data');
        }
      }
      
      if (executionVariables) {
        try {
          variables = JSON.parse(executionVariables);
        } catch (e) {
          throw new Error('Invalid JSON in variables');
        }
      }
      
      const response = await api.post(`/workflow/workflows/${workflowId}/execute`, {
        input_data: inputData,
        variables: variables
      });
      
      // Load executions for this workflow
      await loadExecutions(workflowId);
      setExecutionInput('');
      setExecutionVariables('');
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute workflow');
    } finally {
      setLoading(false);
    }
  };

  const addStep = (stepType) => {
    const newStep = {
      id: `step_${Date.now()}`,
      name: `New ${stepType} Step`,
      type: stepType,
      config: getDefaultConfig(stepType),
      next_step: null,
      error_step: null
    };
    
    setSteps([...steps, newStep]);
    setSelectedStep(newStep);
    setShowStepModal(true);
  };

  const updateStep = (stepId, updates) => {
    setSteps(steps.map(step => 
      step.id === stepId ? { ...step, ...updates } : step
    ));
  };

  const deleteStep = (stepId) => {
    setSteps(steps.filter(step => step.id !== stepId));
    if (selectedStep?.id === stepId) {
      setSelectedStep(null);
    }
  };

  const getDefaultConfig = (stepType) => {
    switch (stepType) {
      case 'llm':
        return {
          prompt: 'Enter your prompt here',
          model: 'gpt-3.5-turbo',
          max_tokens: 1000,
          temperature: 0.7,
          output_key: 'result'
        };
      case 'condition':
        return {
          condition: 'data.value > 10',
          output_key: 'condition_result'
        };
      case 'loop':
        return {
          items: 'data.items',
          steps: [],
          output_key: 'loop_results'
        };
      case 'api_call':
        return {
          url: 'https://api.example.com/endpoint',
          method: 'GET',
          headers: {},
          body: {},
          output_key: 'api_response'
        };
      case 'transform':
        return {
          type: 'map',
          mapping: {},
          output_key: 'transformed'
        };
      default:
        return {};
    }
  };

  const getStepIcon = (stepType) => {
    switch (stepType) {
      case 'llm': return '🤖';
      case 'condition': return '🔀';
      case 'loop': return '🔄';
      case 'api_call': return '🌐';
      case 'transform': return '⚙️';
      default: return '📋';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Workflow Builder</h1>
          <p className="mt-2 text-gray-600">Create and manage multi-step workflows for enterprise automation</p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'builder', name: 'Workflow Builder', icon: '🔧' },
              { id: 'workflows', name: 'My Workflows', icon: '📋' },
              { id: 'executions', name: 'Executions', icon: '▶️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Workflow Builder Tab */}
        {activeTab === 'builder' && !loading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Workflow Form */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Workflow</h3>
                <form onSubmit={handleCreateWorkflow}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Workflow Name
                    </label>
                    <input
                      type="text"
                      value={workflowName}
                      onChange={(e) => setWorkflowName(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={workflowDescription}
                      onChange={(e) => setWorkflowDescription(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows="3"
                    />
                  </div>
                  
                  <button
                    type="submit"
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    Create Workflow
                  </button>
                </form>
              </div>

              {/* Step Types */}
              <div className="bg-white rounded-lg shadow p-6 mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Add Steps</h3>
                <div className="space-y-2">
                  {[
                    { type: 'llm', name: 'LLM Generation', desc: 'Generate text using AI models' },
                    { type: 'condition', name: 'Condition', desc: 'Add conditional logic' },
                    { type: 'loop', name: 'Loop', desc: 'Repeat steps for each item' },
                    { type: 'api_call', name: 'API Call', desc: 'Make external API requests' },
                    { type: 'transform', name: 'Transform', desc: 'Transform data between steps' }
                  ].map((stepType) => (
                    <button
                      key={stepType.type}
                      onClick={() => addStep(stepType.type)}
                      className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">{getStepIcon(stepType.type)}</span>
                        <div>
                          <div className="font-medium text-gray-900">{stepType.name}</div>
                          <div className="text-sm text-gray-500">{stepType.desc}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Workflow Canvas */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Workflow Steps</h3>
                
                {steps.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-6xl mb-4">🔧</div>
                    <p className="text-gray-500">Add steps to build your workflow</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {steps.map((step, index) => (
                      <div
                        key={step.id}
                        className={`p-4 border rounded-lg cursor-pointer ${
                          selectedStep?.id === step.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedStep(step)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="text-2xl mr-3">{getStepIcon(step.type)}</span>
                            <div>
                              <div className="font-medium text-gray-900">{step.name}</div>
                              <div className="text-sm text-gray-500">{step.type}</div>
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteStep(step.id);
                            }}
                            className="text-red-600 hover:text-red-800"
                          >
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Workflows Tab */}
        {activeTab === 'workflows' && !loading && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">My Workflows</h2>
              <button
                onClick={() => setActiveTab('builder')}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Create New Workflow
              </button>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {workflows.map((workflow) => (
                <div key={workflow.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{workflow.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        workflow.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {workflow.status}
                      </span>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedWorkflow(workflow);
                        setActiveTab('executions');
                        loadExecutions(workflow.id);
                      }}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Execute
                    </button>
                  </div>
                  
                  {workflow.description && (
                    <p className="text-gray-600 mb-4">{workflow.description}</p>
                  )}
                  
                  <div className="text-xs text-gray-500">
                    Version: {workflow.version} • Created: {formatDate(workflow.created_at)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Executions Tab */}
        {activeTab === 'executions' && !loading && (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Workflow Executions</h2>
              
              {selectedWorkflow && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Execute: {selectedWorkflow.name}
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Input Data (JSON)
                      </label>
                      <textarea
                        value={executionInput}
                        onChange={(e) => setExecutionInput(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="4"
                        placeholder='{"key": "value"}'
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Variables (JSON)
                      </label>
                      <textarea
                        value={executionVariables}
                        onChange={(e) => setExecutionVariables(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="4"
                        placeholder='{"var1": "value1"}'
                      />
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleExecuteWorkflow(selectedWorkflow.id)}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                  >
                    Execute Workflow
                  </button>
                </div>
              )}
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {executions.map((execution) => (
                  <li key={execution.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-2 h-2 rounded-full mr-3 ${
                          execution.status === 'completed' ? 'bg-green-400' : 
                          execution.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400'
                        }`}></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Execution {execution.id.slice(0, 8)}
                          </p>
                          <p className="text-sm text-gray-500">
                            Started: {formatDate(execution.started_at)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(execution.status)}`}>
                          {execution.status}
                        </span>
                        {execution.execution_time_ms && (
                          <p className="text-xs text-gray-500 mt-1">
                            {execution.execution_time_ms}ms
                          </p>
                        )}
                      </div>
                    </div>
                    {execution.error_message && (
                      <div className="mt-2 text-sm text-red-600">
                        Error: {execution.error_message}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Step Configuration Modal */}
        {showStepModal && selectedStep && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Configure Step</h3>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  setShowStepModal(false);
                }}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Step Name
                    </label>
                    <input
                      type="text"
                      value={selectedStep.name}
                      onChange={(e) => updateStep(selectedStep.id, { name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Configuration (JSON)
                    </label>
                    <textarea
                      value={JSON.stringify(selectedStep.config, null, 2)}
                      onChange={(e) => {
                        try {
                          const config = JSON.parse(e.target.value);
                          updateStep(selectedStep.id, { config });
                        } catch (err) {
                          // Invalid JSON, ignore
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows="8"
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => setShowStepModal(false)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                      Close
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowBuilder; 