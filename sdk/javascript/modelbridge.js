/**
 * Model Bridge JavaScript SDK - Enterprise Edition
 * Supports both Node.js and browser environments
 */

// TypeScript-style enums for JavaScript
const ModelProvider = {
    OPENAI: 'openai',
    ANTHROPIC: 'anthropic',
    GOOGLE: 'google',
    COHERE: 'cohere',
    GROQ: 'groq',
    DEEPSEEK: 'deepseek',
    MISTRAL: 'mistral',
    PERPLEXITY: 'perplexity',
    TOGETHER: 'together',
    HUGGINGFACE: 'huggingface',
    OLLAMA: 'ollama'
};

const WorkflowStatus = {
    DRAFT: 'draft',
    RUNNING: 'running',
    COMPLETED: 'completed',
    FAILED: 'failed',
    CANCELLED: 'cancelled'
};

/**
 * Model response data structure
 */
class ModelResponse {
    constructor(content, model, provider, usage = {}, metadata = {}) {
        this.content = content;
        this.model = model;
        this.provider = provider;
        this.usage = usage;
        this.metadata = metadata;
    }
}

/**
 * Workflow execution data structure
 */
class WorkflowExecution {
    constructor(id, workflowId, status, inputData, outputData, startedAt, completedAt = null, executionTimeMs = null, totalCost = null) {
        this.id = id;
        this.workflowId = workflowId;
        this.status = status;
        this.inputData = inputData;
        this.outputData = outputData;
        this.startedAt = startedAt;
        this.completedAt = completedAt;
        this.executionTimeMs = executionTimeMs;
        this.totalCost = totalCost;
    }
}

/**
 * Enterprise Model Bridge JavaScript SDK Client
 */
class ModelBridgeClient {
    constructor(apiKey, options = {}) {
        this.apiKey = apiKey;
        this.baseUrl = (options.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
        this.organizationId = options.organizationId || null;
        this.timeout = options.timeout || 30000;
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.cache = new Map();
        
        // WebSocket support for real-time features
        this.ws = null;
        this.wsCallbacks = new Map();
    }

    /**
     * Make HTTP request with retry logic
     */
    async _makeRequest(method, endpoint, data = null, params = null) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        
        if (params) {
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined) {
                    url.searchParams.append(key, params[key]);
                }
            });
        }

        const headers = {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
        };

        const config = {
            method,
            headers,
            timeout: this.timeout
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        for (let attempt = 0; attempt < this.maxRetries; attempt++) {
            try {
                const response = await fetch(url.toString(), config);
                
                if (response.ok) {
                    return await response.json();
                } else if (response.status === 401) {
                    throw new Error('Invalid API key');
                } else if (response.status === 403) {
                    throw new Error('Insufficient permissions');
                } else if (response.status === 429) {
                    if (attempt < this.maxRetries - 1) {
                        await this._sleep(this.retryDelay * Math.pow(2, attempt));
                        continue;
                    }
                    throw new Error('Rate limit exceeded');
                } else {
                    const errorData = await response.json();
                    throw new Error(`API error: ${errorData.detail || 'Unknown error'}`);
                }
            } catch (error) {
                if (attempt < this.maxRetries - 1) {
                    await this._sleep(this.retryDelay * Math.pow(2, attempt));
                    continue;
                }
                throw error;
            }
        }
        
        throw new Error('Max retries exceeded');
    }

    /**
     * Sleep utility for retry delays
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Send chat completion request
     */
    async chatCompletion(messages, options = {}) {
        const {
            model = 'gpt-3.5-turbo',
            provider = null,
            temperature = 0.7,
            maxTokens = null,
            stream = false,
            ...otherOptions
        } = options;

        const data = {
            messages,
            model,
            temperature,
            stream,
            ...otherOptions
        };

        if (provider) {
            data.provider = provider;
        }

        if (maxTokens) {
            data.max_tokens = maxTokens;
        }

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        const response = await this._makeRequest('POST', '/api/llm/chat', data);
        
        return new ModelResponse(
            response.choices[0].message.content,
            response.model,
            response.provider || 'unknown',
            response.usage || {},
            response.metadata || {}
        );
    }

    /**
     * Send completion request
     */
    async completion(prompt, options = {}) {
        const {
            model = 'gpt-3.5-turbo',
            provider = null,
            temperature = 0.7,
            maxTokens = null,
            ...otherOptions
        } = options;

        const data = {
            prompt,
            model,
            temperature,
            ...otherOptions
        };

        if (provider) {
            data.provider = provider;
        }

        if (maxTokens) {
            data.max_tokens = maxTokens;
        }

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        const response = await this._makeRequest('POST', '/api/llm/completion', data);
        
        return new ModelResponse(
            response.choices[0].text,
            response.model,
            response.provider || 'unknown',
            response.usage || {},
            response.metadata || {}
        );
    }

    /**
     * Get available models
     */
    async getModels() {
        const response = await this._makeRequest('GET', '/api/llm/models');
        return response.models || [];
    }

    /**
     * Get available providers
     */
    async getProviders() {
        const response = await this._makeRequest('GET', '/api/llm/providers');
        return response.providers || [];
    }

    /**
     * Create a new workflow
     */
    async createWorkflow(name, definition, description = null) {
        const data = {
            name,
            definition
        };

        if (description) {
            data.description = description;
        }

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        return await this._makeRequest('POST', '/api/workflows', data);
    }

    /**
     * Execute a workflow
     */
    async executeWorkflow(workflowId, inputData) {
        const data = {
            workflow_id: workflowId,
            input_data: inputData
        };

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        const response = await this._makeRequest('POST', '/api/workflows/execute', data);
        
        return new WorkflowExecution(
            response.id,
            response.workflow_id,
            response.status,
            response.input_data,
            response.output_data || {},
            new Date(response.started_at),
            response.completed_at ? new Date(response.completed_at) : null,
            response.execution_time_ms,
            response.total_cost
        );
    }

    /**
     * Get workflow execution status
     */
    async getWorkflowExecution(executionId) {
        const response = await this._makeRequest('GET', `/api/workflows/executions/${executionId}`);
        
        return new WorkflowExecution(
            response.id,
            response.workflow_id,
            response.status,
            response.input_data,
            response.output_data || {},
            new Date(response.started_at),
            response.completed_at ? new Date(response.completed_at) : null,
            response.execution_time_ms,
            response.total_cost
        );
    }

    /**
     * Get usage analytics
     */
    async getUsageAnalytics(options = {}) {
        const {
            startDate = null,
            endDate = null,
            groupBy = null
        } = options;

        const params = {};

        if (startDate) {
            params.start_date = startDate.toISOString();
        }

        if (endDate) {
            params.end_date = endDate.toISOString();
        }

        if (groupBy) {
            params.group_by = groupBy;
        }

        if (this.organizationId) {
            params.organization_id = this.organizationId;
        }

        return await this._makeRequest('GET', '/api/analytics/usage', null, params);
    }

    /**
     * Get cost analytics
     */
    async getCostAnalytics(options = {}) {
        const {
            startDate = null,
            endDate = null,
            costCenter = null
        } = options;

        const params = {};

        if (startDate) {
            params.start_date = startDate.toISOString();
        }

        if (endDate) {
            params.end_date = endDate.toISOString();
        }

        if (costCenter) {
            params.cost_center = costCenter;
        }

        if (this.organizationId) {
            params.organization_id = this.organizationId;
        }

        return await this._makeRequest('GET', '/api/analytics/costs', null, params);
    }

    /**
     * Get audit logs
     */
    async getAuditLogs(options = {}) {
        const {
            startDate = null,
            endDate = null,
            userId = null,
            action = null,
            limit = 100
        } = options;

        const params = { limit };

        if (startDate) {
            params.start_date = startDate.toISOString();
        }

        if (endDate) {
            params.end_date = endDate.toISOString();
        }

        if (userId) {
            params.user_id = userId;
        }

        if (action) {
            params.action = action;
        }

        if (this.organizationId) {
            params.organization_id = this.organizationId;
        }

        const response = await this._makeRequest('GET', '/api/audit/logs', null, params);
        return response.logs || [];
    }

    /**
     * Create a new role
     */
    async createRole(name, permissions, description = null) {
        const data = {
            name,
            permissions
        };

        if (description) {
            data.description = description;
        }

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        return await this._makeRequest('POST', '/api/rbac/roles', data);
    }

    /**
     * Assign role to user
     */
    async assignRole(userId, roleId) {
        const data = {
            user_id: userId,
            role_id: roleId
        };

        if (this.organizationId) {
            data.organization_id = this.organizationId;
        }

        return await this._makeRequest('POST', '/api/rbac/assignments', data);
    }

    /**
     * Get all roles
     */
    async getRoles() {
        const params = {};

        if (this.organizationId) {
            params.organization_id = this.organizationId;
        }

        const response = await this._makeRequest('GET', '/api/rbac/roles', null, params);
        return response.roles || [];
    }

    /**
     * Get all permissions
     */
    async getPermissions() {
        const response = await this._makeRequest('GET', '/api/rbac/permissions');
        return response.permissions || [];
    }

    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket() {
        if (typeof WebSocket === 'undefined') {
            throw new Error('WebSocket not available in this environment');
        }

        const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws';
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            // Send authentication
            this.ws.send(JSON.stringify({
                type: 'auth',
                api_key: this.apiKey
            }));
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._handleWebSocketMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    /**
     * Handle WebSocket messages
     */
    _handleWebSocketMessage(data) {
        const { type, payload } = data;
        
        if (this.wsCallbacks.has(type)) {
            this.wsCallbacks.get(type).forEach(callback => {
                try {
                    callback(payload);
                } catch (error) {
                    console.error('WebSocket callback error:', error);
                }
            });
        }
    }

    /**
     * Subscribe to WebSocket events
     */
    on(event, callback) {
        if (!this.wsCallbacks.has(event)) {
            this.wsCallbacks.set(event, []);
        }
        this.wsCallbacks.get(event).push(callback);
    }

    /**
     * Unsubscribe from WebSocket events
     */
    off(event, callback) {
        if (this.wsCallbacks.has(event)) {
            const callbacks = this.wsCallbacks.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    /**
     * Close WebSocket connection
     */
    disconnectWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

/**
 * Create a Model Bridge client
 */
function createClient(apiKey, options = {}) {
    return new ModelBridgeClient(apiKey, options);
}

/**
 * Quick chat completion function
 */
async function chatCompletion(apiKey, messages, options = {}) {
    const client = createClient(apiKey);
    return await client.chatCompletion(messages, options);
}

/**
 * Quick completion function
 */
async function completion(apiKey, prompt, options = {}) {
    const client = createClient(apiKey);
    return await client.completion(prompt, options);
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = {
        ModelBridgeClient,
        ModelResponse,
        WorkflowExecution,
        ModelProvider,
        WorkflowStatus,
        createClient,
        chatCompletion,
        completion
    };
} else if (typeof window !== 'undefined') {
    // Browser
    window.ModelBridge = {
        ModelBridgeClient,
        ModelResponse,
        WorkflowExecution,
        ModelProvider,
        WorkflowStatus,
        createClient,
        chatCompletion,
        completion
    };
} 