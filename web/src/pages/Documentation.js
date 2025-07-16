import React, { useState } from 'react';
import { 
  BookOpenIcon, 
  CodeBracketIcon,
  KeyIcon, 
  CpuChipIcon,
  DocumentTextIcon,
  PlayIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ChevronRightIcon,
  StarIcon,
  BoltIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CogIcon,
  ServerIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Documentation = () => {
  const [activeTab, setActiveTab] = useState('quickstart');
  const [activeLanguage, setActiveLanguage] = useState('python');

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const CodeBlock = ({ code, language = 'javascript', id, title }) => {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = () => {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };

    return (
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {title && (
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <h4 className="text-sm font-medium text-gray-700">{title}</h4>
          </div>
        )}
        <div className="relative">
          <button
            onClick={handleCopy}
            className="absolute top-3 right-3 p-2 text-gray-400 hover:text-gray-600 transition-colors z-10"
            title="Copy code"
          >
            {copied ? (
              <CheckIcon className="h-4 w-4 text-green-500" />
            ) : (
              <ClipboardDocumentIcon className="h-4 w-4" />
            )}
          </button>
          <pre className="p-4 bg-gray-50 overflow-x-auto max-h-96 overflow-y-auto">
            <code className={`text-sm ${language === 'python' ? 'text-blue-800' : language === 'javascript' ? 'text-yellow-800' : 'text-gray-800'}`}>
              {code}
            </code>
          </pre>
        </div>
      </div>
    );
  };

  const LanguageTabs = ({ languages, activeLanguage, onLanguageChange }) => (
    <div className="flex border-b border-gray-200 mb-4">
      {languages.map((lang) => (
        <button
          key={lang.key}
          onClick={() => onLanguageChange(lang.key)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeLanguage === lang.key
              ? 'border-b-2 border-[#9B5967] text-[#9B5967]'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {lang.label}
        </button>
      ))}
      </div>
  );

  const codeExamples = {
    quickstart: {
      python: `from model_bridge import ModelBridge

# Initialize the client
client = ModelBridge(
    api_key="YOUR_API_KEY",
    base_url="https://api.modelbridge.com/v1"
)

# Make your first request
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ]
)

print(response.choices[0].message.content)`,
      
      typescript: `import { ModelBridge } from '@model-bridge/client';

// Initialize the client
const client = new ModelBridge({
  apiKey: 'YOUR_API_KEY',
  baseURL: 'https://api.modelbridge.com/v1'
});

// Make your first request
const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [
    { role: 'user', content: 'Hello! How are you?' }
  ]
});

console.log(response.choices[0].message.content);`,
      
      javascript: `import { ModelBridge } from '@model-bridge/client';

// Initialize the client
const client = new ModelBridge({
  apiKey: 'YOUR_API_KEY',
  baseURL: 'https://api.modelbridge.com/v1'
});

// Make your first request
const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [
    { role: 'user', content: 'Hello! How are you?' }
  ]
});

console.log(response.choices[0].message.content);`,
      
      curl: `curl -X POST "https://api.modelbridge.com/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello! How are you?"
      }
    ]
  }'`
    },
    
    authentication: {
      python: `# Set your API key as an environment variable
import os
os.environ["MODELBRIDGE_API_KEY"] = "your-api-key-here"

# Or pass it directly to the client
from model_bridge import ModelBridge

client = ModelBridge(api_key="your-api-key-here")`,
      
      typescript: `// Set your API key as an environment variable
process.env.MODELBRIDGE_API_KEY = 'your-api-key-here';

// Or pass it directly to the client
import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({
  apiKey: 'your-api-key-here'
});`,
      
      javascript: `// Set your API key as an environment variable
process.env.MODELBRIDGE_API_KEY = 'your-api-key-here';

// Or pass it directly to the client
import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({
  apiKey: 'your-api-key-here'
});`,
      
      curl: `# Set your API key as an environment variable
export MODELBRIDGE_API_KEY="your-api-key-here"

# Use it in your requests
curl -X POST "https://api.modelbridge.com/v1/chat/completions" \\
  -H "Authorization: Bearer \$MODELBRIDGE_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'`
    },
    
    streaming: {
      python: `from model_bridge import ModelBridge

client = ModelBridge(api_key="YOUR_API_KEY")

# Stream the response
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')`,
      
      typescript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// Stream the response
const stream = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Tell me a story' }],
  stream: true
});

for await (const chunk of stream) {
  if (chunk.choices[0].delta.content) {
    process.stdout.write(chunk.choices[0].delta.content);
  }
}`,
      
      javascript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// Stream the response
const stream = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Tell me a story' }],
  stream: true
});

for await (const chunk of stream) {
  if (chunk.choices[0].delta.content) {
    process.stdout.write(chunk.choices[0].delta.content);
  }
}`,
      
      curl: `curl -X POST "https://api.modelbridge.com/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Tell me a story"
      }
    ],
    "stream": true
  }'`
    },
    
    models: {
      python: `from model_bridge import ModelBridge

client = ModelBridge(api_key="YOUR_API_KEY")

# List available models
models = client.models.list()
for model in models.data:
    print(f"Model: {model.id}")
    print(f"Provider: {model.provider}")
    print(f"Context Length: {model.context_length}")
    print("---")`,
      
      typescript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// List available models
const models = await client.models.list();
for (const model of models.data) {
  console.log(\`Model: \${model.id}\`);
  console.log(\`Provider: \${model.provider}\`);
  console.log(\`Context: \${model.context_length}\`);
  console.log('---');
}`,
      
      javascript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// List available models
const models = await client.models.list();
for (const model of models.data) {
  console.log(\`Model: \${model.id}\`);
  console.log(\`Provider: \${model.provider}\`);
  console.log(\`Context: \${model.context_length}\`);
  console.log('---');
}`,
      
      curl: `curl -X GET "https://api.modelbridge.com/v1/models" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`

    },
    
    structured_output: {
      python: `from model_bridge import ModelBridge
import json

client = ModelBridge(api_key="YOUR_API_KEY")

# Define the schema for structured output
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "city": {"type": "string"}
    }
}

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Extract John's information: John is 25 years old and lives in New York."}],
    response_format={"type": "json_object"},
    tools=[{"type": "function", "function": {"name": "extract_info", "parameters": schema}}]
)

print(json.loads(response.choices[0].message.content))`,
      
      typescript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// Define the schema for structured output
const schema = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    age: { type: 'integer' },
    city: { type: 'string' }
  }
};

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Extract John\'s information: John is 25 years old and lives in New York.' }],
  response_format: { type: 'json_object' },
  tools: [{ type: 'function', function: { name: 'extract_info', parameters: schema } }]
});

console.log(JSON.parse(response.choices[0].message.content));`,
      
      javascript: `import { ModelBridge } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

// Define the schema for structured output
const schema = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    age: { type: 'integer' },
    city: { type: 'string' }
  }
};

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Extract John\'s information: John is 25 years old and lives in New York.' }],
  response_format: { type: 'json_object' },
  tools: [{ type: 'function', function: { name: 'extract_info', parameters: schema } }]
});

console.log(JSON.parse(response.choices[0].message.content));`,
      
             curl: `curl -X POST "https://api.modelbridge.com/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Extract John information: John is 25 years old and lives in New York."
      }
    ],
    "response_format": {"type": "json_object"},
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "extract_info",
          "parameters": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "age": {"type": "integer"},
              "city": {"type": "string"}
            }
          }
        }
      }
    ]
  }'`
    },
    
    error_handling: {
      python: `from model_bridge import ModelBridge
from model_bridge.errors import ModelBridgeError, RateLimitError

client = ModelBridge(api_key="YOUR_API_KEY")

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Wait and retry
    import time
    time.sleep(e.retry_after)
    
except ModelBridgeError as e:
    print(f"API error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")`,
      
      typescript: `import { ModelBridge, ModelBridgeError, RateLimitError } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

try {
  const response = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello!' }]
  });
  console.log(response.choices[0].message.content);
  
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(\`Rate limit exceeded: \${error}\`);
    // Wait and retry
    await new Promise(resolve => setTimeout(resolve, error.retryAfter * 1000));
  } else if (error instanceof ModelBridgeError) {
    console.log(\`API error: \${error}\`);
  } else {
    console.log(\`Unexpected error: \${error}\`);
  }
}`,
      
      javascript: `import { ModelBridge, ModelBridgeError, RateLimitError } from '@model-bridge/client';

const client = new ModelBridge({ apiKey: 'YOUR_API_KEY' });

try {
  const response = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello!' }]
  });
  console.log(response.choices[0].message.content);
  
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(\`Rate limit exceeded: \${error}\`);
    // Wait and retry
    await new Promise(resolve => setTimeout(resolve, error.retryAfter * 1000));
  } else if (error instanceof ModelBridgeError) {
    console.log(\`API error: \${error}\`);
  } else {
    console.log(\`Unexpected error: \${error}\`);
  }
}`,
      
      curl: `# Handle errors in curl
response=$(curl -s -w "%{http_code}" -X POST "https://api.modelbridge.com/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }')

http_code="\${response: -3}"
body="\${response%???}"

if [ "\$http_code" = "200" ]; then
    echo "Success: \$body"
else
    echo "Error (\$http_code): \$body"
fi`
    }
  };

  const languages = [
    { key: 'python', label: 'Python' },
    { key: 'typescript', label: 'TypeScript' },
    { key: 'javascript', label: 'JavaScript' },
    { key: 'curl', label: 'cURL' }
  ];

  const tabs = [
    { id: 'quickstart', label: 'Quick Start', icon: PlayIcon },
    { id: 'authentication', label: 'Authentication', icon: KeyIcon },
    { id: 'models', label: 'Models', icon: CpuChipIcon },
    { id: 'streaming', label: 'Streaming', icon: BoltIcon },
    { id: 'structured_output', label: 'Structured Output', icon: DocumentTextIcon },
    { id: 'error_handling', label: 'Error Handling', icon: ExclamationTriangleIcon }
  ];

  const renderQuickStart = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Get Started in Minutes</h2>
        <p className="text-gray-600 mb-6">
          Model Bridge provides a unified API for accessing 50+ AI models from leading providers. 
          Get started with a simple API call.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <BookOpenIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Before you begin</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>1. Sign up for a free account at <a href="/register" className="underline">Model Bridge</a></p>
              <p>2. Get your API key from the <a href="/dashboard/api-keys" className="underline">API Keys</a> page</p>
              <p>3. Choose your preferred programming language below</p>
            </div>
          </div>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.quickstart[activeLanguage]} 
        language={activeLanguage}
        title="Your First API Call"
      />

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <CheckIcon className="h-5 w-5 text-green-600" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">Success!</h3>
            <p className="text-sm text-green-700 mt-1">
              You've made your first API call to Model Bridge. The response will contain the AI model's reply.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAuthentication = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication</h2>
        <p className="text-gray-600 mb-6">
          All API requests require authentication using your API key. You can set it as an environment variable 
          or pass it directly to the client.
        </p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Security Best Practices</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>• Never commit API keys to version control</p>
              <p>• Use environment variables in production</p>
              <p>• Rotate keys regularly for security</p>
            </div>
          </div>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.authentication[activeLanguage]} 
        language={activeLanguage}
        title="Setting Up Authentication"
      />
    </div>
  );

  const renderModels = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Models</h2>
        <p className="text-gray-600 mb-6">
          Model Bridge provides access to 50+ models from leading AI providers. Each model has different 
          capabilities, pricing, and performance characteristics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Model Categories</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• GPT-4 and GPT-3.5 (OpenAI)</li>
            <li>• Claude 3 (Anthropic)</li>
            <li>• Gemini (Google)</li>
            <li>• Llama models (Meta)</li>
            <li>• And many more...</li>
          </ul>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Model Selection</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Choose based on your use case</li>
            <li>• Consider cost vs. performance</li>
            <li>• Check context length limits</li>
            <li>• Test different models</li>
          </ul>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.models[activeLanguage]} 
        language={activeLanguage}
        title="Listing Available Models"
      />
    </div>
  );

  const renderStreaming = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Streaming Responses</h2>
        <p className="text-gray-600 mb-6">
          Stream responses in real-time for better user experience. This is especially useful for 
          long-form content generation and chat applications.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <BoltIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Streaming Benefits</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>• Real-time response display</p>
              <p>• Better user experience</p>
              <p>• Reduced perceived latency</p>
              <p>• Progressive content loading</p>
            </div>
          </div>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.streaming[activeLanguage]} 
        language={activeLanguage}
        title="Streaming API Responses"
      />
    </div>
  );

  const renderStructuredOutput = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Structured Output</h2>
        <p className="text-gray-600 mb-6">
          Get structured, predictable outputs from AI models. Perfect for data extraction, 
          form processing, and API integrations.
        </p>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <DocumentTextIcon className="h-5 w-5 text-purple-600" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-purple-800">Use Cases</h3>
            <div className="mt-2 text-sm text-purple-700">
              <p>• Data extraction from documents</p>
              <p>• Form processing and validation</p>
              <p>• API response formatting</p>
              <p>• Database record creation</p>
            </div>
          </div>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.structured_output[activeLanguage]} 
        language={activeLanguage}
        title="Structured Output Example"
      />
    </div>
  );

  const renderErrorHandling = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Error Handling</h2>
        <p className="text-gray-600 mb-6">
          Learn how to handle different types of errors gracefully in your applications. 
          Proper error handling ensures your app remains robust and user-friendly.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-900 mb-2">Rate Limits</h3>
          <p className="text-sm text-red-700">Handle when you exceed API rate limits</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="font-semibold text-orange-900 mb-2">API Errors</h3>
          <p className="text-sm text-orange-700">Handle server errors and invalid requests</p>
        </div>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Network Issues</h3>
          <p className="text-sm text-gray-700">Handle connection timeouts and network failures</p>
        </div>
      </div>

      <LanguageTabs 
        languages={languages} 
        activeLanguage={activeLanguage} 
        onLanguageChange={setActiveLanguage} 
      />

      <CodeBlock 
        code={codeExamples.error_handling[activeLanguage]} 
        language={activeLanguage}
        title="Error Handling Example"
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-full mx-auto px-2 sm:px-4 lg:px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Sidebar - Moved closer to left */}
          <div className="lg:w-56 flex-shrink-0">
            <div className="sticky top-24">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                        activeTab === tab.id
                          ? 'bg-[#9B5967] text-white'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {tab.label}
                    </button>
                  );
                })}
              </nav>

              <div className="mt-6 p-3 bg-white border border-gray-200 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Need Help?</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <p>• <a href="/pricing" className="text-[#9B5967] hover:underline">View Pricing</a></p>
                  <p>• <a href="/models" className="text-[#9B5967] hover:underline">Browse Models</a></p>
                  <p>• <a href="/register" className="text-[#9B5967] hover:underline">Get API Key</a></p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Adjusted for better fit */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 lg:p-8">
              {activeTab === 'quickstart' && renderQuickStart()}
              {activeTab === 'authentication' && renderAuthentication()}
              {activeTab === 'models' && renderModels()}
              {activeTab === 'streaming' && renderStreaming()}
              {activeTab === 'structured_output' && renderStructuredOutput()}
              {activeTab === 'error_handling' && renderErrorHandling()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documentation;