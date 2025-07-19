"""
Interactive API Playground - Phase 4.1: Interactive API Playground

This module provides a comprehensive API playground with:
- Real-time API testing interface
- Code generation for multiple languages
- Request/response visualization
- Authentication testing
- Error handling demonstration
"""

import json
import uuid
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class CodeLanguage(Enum):
    """Supported code generation languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CURL = "curl"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: HTTPMethod
    name: str
    description: str
    parameters: Dict[str, Any]
    request_body: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    auth_required: bool = True
    examples: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class PlaygroundRequest:
    """Playground API request"""
    id: str
    endpoint: APIEndpoint
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    auth_config: Dict[str, str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class PlaygroundResponse:
    """Playground API response"""
    id: str
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any
    response_time_ms: int
    timestamp: datetime = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class CodeGenerator:
    """
    Advanced code generation engine for multiple programming languages.
    
    Generates production-ready code examples with:
    - Error handling
    - Authentication
    - Best practices
    - Documentation
    """
    
    def __init__(self):
        """Initialize the code generator."""
        self.generators = {
            CodeLanguage.PYTHON: self._generate_python_code,
            CodeLanguage.JAVASCRIPT: self._generate_javascript_code,
            CodeLanguage.TYPESCRIPT: self._generate_typescript_code,
            CodeLanguage.CURL: self._generate_curl_code,
            CodeLanguage.GO: self._generate_go_code,
            CodeLanguage.JAVA: self._generate_java_code,
            CodeLanguage.CSHARP: self._generate_csharp_code,
            CodeLanguage.PHP: self._generate_php_code,
            CodeLanguage.RUBY: self._generate_ruby_code
        }
    
    def generate_code(
        self, 
        request: PlaygroundRequest, 
        language: CodeLanguage,
        include_auth: bool = True,
        include_error_handling: bool = True
    ) -> str:
        """
        Generate code for API request in specified language.
        
        Args:
            request: Playground request to generate code for
            language: Target programming language
            include_auth: Include authentication handling
            include_error_handling: Include error handling
            
        Returns:
            str: Generated code
        """
        
        generator = self.generators.get(language)
        if not generator:
            raise ValueError(f"Unsupported language: {language}")
        
        return generator(request, include_auth, include_error_handling)
    
    def _generate_python_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate Python code using requests library."""
        
        imports = ["import requests", "import json"]
        if include_error_handling:
            imports.append("from requests.exceptions import RequestException")
        
        code = "\n".join(imports) + "\n\n"
        
        # API configuration
        base_url = "https://api.llmgateway.com"  # Replace with actual base URL
        code += f'base_url = "{base_url}"\n'
        code += f'endpoint = "{request.endpoint.path}"\n'
        code += f'url = base_url + endpoint\n\n'
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        code += f"headers = {json.dumps(headers, indent=4)}\n\n"
        
        # Query parameters
        if request.query_params:
            code += f"params = {json.dumps(request.query_params, indent=4)}\n\n"
        
        # Request body
        if request.body:
            code += f"data = {json.dumps(request.body, indent=4)}\n\n"
        
        # Make request
        if include_error_handling:
            code += "try:\n    "
        
        method = request.endpoint.method.value.lower()
        request_args = ["url", "headers=headers"]
        
        if request.query_params:
            request_args.append("params=params")
        
        if request.body:
            request_args.append("json=data")
        
        code += f"response = requests.{method}({', '.join(request_args)})\n"
        
        if include_error_handling:
            code += "    response.raise_for_status()\n"
            code += "    \n"
            code += "    # Parse response\n"
            code += "    result = response.json()\n"
            code += "    print(f\"Success: {result}\")\n"
            code += "    \n"
            code += "except RequestException as e:\n"
            code += "    print(f\"Request failed: {e}\")\n"
            code += "except json.JSONDecodeError as e:\n"
            code += "    print(f\"Failed to parse response: {e}\")\n"
        else:
            code += "\n# Parse response\n"
            code += "result = response.json()\n"
            code += "print(result)\n"
        
        return code
    
    def _generate_javascript_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate JavaScript code using fetch API."""
        
        code = "// JavaScript implementation using fetch API\n\n"
        
        # API configuration
        base_url = "https://api.llmgateway.com"
        code += f'const baseUrl = "{base_url}";\n'
        code += f'const endpoint = "{request.endpoint.path}";\n'
        code += f'const url = baseUrl + endpoint;\n\n'
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        code += f"const headers = {json.dumps(headers, indent=2)};\n\n"
        
        # Request configuration
        config = {
            "method": request.endpoint.method.value,
            "headers": "headers"
        }
        
        if request.body:
            code += f"const data = {json.dumps(request.body, indent=2)};\n\n"
            config["body"] = "JSON.stringify(data)"
        
        # Add query parameters to URL if present
        if request.query_params:
            code += f"const params = new URLSearchParams({json.dumps(request.query_params)});\n"
            code += f"const fullUrl = url + '?' + params.toString();\n\n"
            url_var = "fullUrl"
        else:
            url_var = "url"
        
        # Make request
        if include_error_handling:
            code += "async function makeRequest() {\n"
            code += "  try {\n    "
        
        config_str = "{\n"
        for key, value in config.items():
            if key == "headers" or key == "body":
                config_str += f"    {key}: {value},\n"
            else:
                config_str += f"    {key}: '{value}',\n"
        config_str += "  }"
        
        code += f"const response = await fetch({url_var}, {config_str});\n"
        
        if include_error_handling:
            code += "    \n"
            code += "    if (!response.ok) {\n"
            code += "      throw new Error(`HTTP error! status: ${response.status}`);\n"
            code += "    }\n"
            code += "    \n"
            code += "    const result = await response.json();\n"
            code += "    console.log('Success:', result);\n"
            code += "    return result;\n"
            code += "    \n"
            code += "  } catch (error) {\n"
            code += "    console.error('Request failed:', error);\n"
            code += "    throw error;\n"
            code += "  }\n"
            code += "}\n\n"
            code += "// Call the function\n"
            code += "makeRequest();"
        else:
            code += "\n// Parse response\n"
            code += "const result = await response.json();\n"
            code += "console.log(result);"
        
        return code
    
    def _generate_typescript_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate TypeScript code with type definitions."""
        
        code = "// TypeScript implementation with type definitions\n\n"
        
        # Type definitions
        code += "interface APIResponse<T = any> {\n"
        code += "  success: boolean;\n"
        code += "  data: T;\n"
        code += "  message?: string;\n"
        code += "}\n\n"
        
        if request.body:
            code += "interface RequestData {\n"
            for key, value in request.body.items():
                type_hint = self._infer_typescript_type(value)
                code += f"  {key}: {type_hint};\n"
            code += "}\n\n"
        
        # API configuration
        base_url = "https://api.llmgateway.com"
        code += f'const baseUrl: string = "{base_url}";\n'
        code += f'const endpoint: string = "{request.endpoint.path}";\n'
        code += f'const url: string = baseUrl + endpoint;\n\n'
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        code += f"const headers: Record<string, string> = {json.dumps(headers, indent=2)};\n\n"
        
        # Request function
        if include_error_handling:
            code += f"async function makeRequest(): Promise<APIResponse> {{\n"
            code += "  try {\n    "
        else:
            code += f"async function makeRequest(): Promise<APIResponse> {{\n  "
        
        # Request configuration
        config = {
            "method": request.endpoint.method.value,
            "headers": "headers"
        }
        
        if request.body:
            code += f"const data: RequestData = {json.dumps(request.body, indent=4)};\n    "
            config["body"] = "JSON.stringify(data)"
        
        # Add query parameters if present
        if request.query_params:
            code += f"const params = new URLSearchParams({json.dumps(request.query_params)});\n    "
            code += f"const fullUrl = url + '?' + params.toString();\n    "
            url_var = "fullUrl"
        else:
            url_var = "url"
        
        config_str = "{\n"
        for key, value in config.items():
            if key == "headers" or key == "body":
                config_str += f"      {key}: {value},\n"
            else:
                config_str += f"      {key}: '{value}',\n"
        config_str += "    }"
        
        code += f"const response = await fetch({url_var}, {config_str});\n"
        
        if include_error_handling:
            code += "    \n"
            code += "    if (!response.ok) {\n"
            code += "      throw new Error(`HTTP error! status: ${response.status}`);\n"
            code += "    }\n"
            code += "    \n"
            code += "    const result: APIResponse = await response.json();\n"
            code += "    console.log('Success:', result);\n"
            code += "    return result;\n"
            code += "    \n"
            code += "  } catch (error) {\n"
            code += "    console.error('Request failed:', error);\n"
            code += "    throw error;\n"
            code += "  }\n"
            code += "}\n\n"
        else:
            code += "  \n"
            code += "  const result: APIResponse = await response.json();\n"
            code += "  console.log(result);\n"
            code += "  return result;\n"
            code += "}\n\n"
        
        code += "// Call the function\n"
        code += "makeRequest();"
        
        return code
    
    def _generate_curl_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate cURL command."""
        
        base_url = "https://api.llmgateway.com"
        url = base_url + request.endpoint.path
        
        # Add query parameters to URL
        if request.query_params:
            params = "&".join([f"{k}={v}" for k, v in request.query_params.items()])
            url += f"?{params}"
        
        curl_parts = [f"curl -X {request.endpoint.method.value}"]
        curl_parts.append(f"'{url}'")
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        for key, value in headers.items():
            curl_parts.append(f"-H '{key}: {value}'")
        
        # Request body
        if request.body:
            body_json = json.dumps(request.body)
            curl_parts.append(f"-d '{body_json}'")
        
        # Add error handling options
        if include_error_handling:
            curl_parts.extend(["-w '\\nStatus: %{http_code}\\n'", "-s", "-S"])
        
        return " \\\n  ".join(curl_parts)
    
    def _generate_go_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate Go code."""
        
        code = "package main\n\n"
        code += "import (\n"
        code += "    \"bytes\"\n"
        code += "    \"encoding/json\"\n"
        code += "    \"fmt\"\n"
        code += "    \"net/http\"\n"
        code += "    \"net/url\"\n"
        if include_error_handling:
            code += "    \"log\"\n"
        code += ")\n\n"
        
        code += "func main() {\n"
        base_url = "https://api.llmgateway.com"
        code += f'    baseURL := "{base_url}"\n'
        code += f'    endpoint := "{request.endpoint.path}"\n'
        code += f'    fullURL := baseURL + endpoint\n\n'
        
        # Add query parameters
        if request.query_params:
            code += "    // Add query parameters\n"
            code += "    params := url.Values{}\n"
            for key, value in request.query_params.items():
                code += f'    params.Add("{key}", "{value}")\n'
            code += "    fullURL += \"?\" + params.Encode()\n\n"
        
        # Request body
        if request.body:
            code += "    // Request body\n"
            code += f"    data := {json.dumps(request.body)}\n"
            code += "    jsonData, _ := json.Marshal(data)\n"
            code += "    req, err := http.NewRequest(\"{}\", fullURL, bytes.NewBuffer(jsonData))\n".format(request.endpoint.method.value)
        else:
            code += f"    req, err := http.NewRequest(\"{request.endpoint.method.value}\", fullURL, nil)\n"
        
        if include_error_handling:
            code += "    if err != nil {\n"
            code += "        log.Fatal(err)\n"
            code += "    }\n\n"
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        for key, value in headers.items():
            code += f'    req.Header.Set("{key}", "{value}")\n'
        
        code += "\n    client := &http.Client{}\n"
        code += "    resp, err := client.Do(req)\n"
        
        if include_error_handling:
            code += "    if err != nil {\n"
            code += "        log.Fatal(err)\n"
            code += "    }\n"
            code += "    defer resp.Body.Close()\n\n"
            code += "    var result map[string]interface{}\n"
            code += "    json.NewDecoder(resp.Body).Decode(&result)\n"
            code += "    fmt.Printf(\"Response: %+v\\n\", result)\n"
        else:
            code += "    defer resp.Body.Close()\n"
            code += "    fmt.Println(\"Request completed\")\n"
        
        code += "}\n"
        
        return code
    
    def _generate_java_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate Java code using HttpClient."""
        
        code = "import java.net.http.HttpClient;\n"
        code += "import java.net.http.HttpRequest;\n"
        code += "import java.net.http.HttpResponse;\n"
        code += "import java.net.URI;\n"
        code += "import java.time.Duration;\n"
        if include_error_handling:
            code += "import java.io.IOException;\n"
            code += "import java.lang.InterruptedException;\n"
        code += "\n"
        
        code += "public class APIClient {\n"
        code += "    public static void main(String[] args) {\n"
        
        if include_error_handling:
            code += "        try {\n            "
        else:
            code += "        "
        
        base_url = "https://api.llmgateway.com"
        code += f'String baseUrl = "{base_url}";\n'
        code += f'            String endpoint = "{request.endpoint.path}";\n'
        code += f'            String url = baseUrl + endpoint;\n\n'
        
        # Request builder
        code += "            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()\n"
        code += "                .uri(URI.create(url))\n"
        code += f"                .{request.endpoint.method.value}()\n"
        code += "                .timeout(Duration.ofSeconds(30))\n"
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        for key, value in headers.items():
            code += f'                .header("{key}", "{value}")\n'
        
        # Request body
        if request.body:
            body_json = json.dumps(request.body)
            code += f'                .POST(HttpRequest.BodyPublishers.ofString("{body_json}"));\n\n'
        else:
            code += ";\n\n"
        
        code += "            HttpClient client = HttpClient.newHttpClient();\n"
        code += "            HttpResponse<String> response = client.send(\n"
        code += "                requestBuilder.build(),\n"
        code += "                HttpResponse.BodyHandlers.ofString()\n"
        code += "            );\n\n"
        
        code += "            System.out.println(\"Status: \" + response.statusCode());\n"
        code += "            System.out.println(\"Response: \" + response.body());\n"
        
        if include_error_handling:
            code += "        } catch (IOException | InterruptedException e) {\n"
            code += "            System.err.println(\"Request failed: \" + e.getMessage());\n"
            code += "        }\n"
        
        code += "    }\n"
        code += "}\n"
        
        return code
    
    def _generate_csharp_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate C# code using HttpClient."""
        
        code = "using System;\n"
        code += "using System.Net.Http;\n"
        code += "using System.Text;\n"
        code += "using System.Threading.Tasks;\n"
        code += "using Newtonsoft.Json;\n\n"
        
        code += "class Program\n"
        code += "{\n"
        code += "    private static readonly HttpClient client = new HttpClient();\n\n"
        
        code += "    static async Task Main(string[] args)\n"
        code += "    {\n"
        
        if include_error_handling:
            code += "        try\n"
            code += "        {\n            "
        else:
            code += "        "
        
        base_url = "https://api.llmgateway.com"
        code += f'string baseUrl = "{base_url}";\n'
        code += f'            string endpoint = "{request.endpoint.path}";\n'
        code += f'            string url = baseUrl + endpoint;\n\n'
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        for key, value in headers.items():
            code += f'            client.DefaultRequestHeaders.Add("{key}", "{value}");\n'
        
        # Request
        if request.body:
            body_json = json.dumps(request.body)
            code += f'\n            string jsonData = @"{body_json}";\n'
            code += "            var content = new StringContent(jsonData, Encoding.UTF8, \"application/json\");\n"
            
            method = request.endpoint.method.value.title()
            if method == "Post":
                code += "            HttpResponseMessage response = await client.PostAsync(url, content);\n"
            elif method == "Put":
                code += "            HttpResponseMessage response = await client.PutAsync(url, content);\n"
            else:
                code += f"            // {method} with content\n"
                code += "            var request = new HttpRequestMessage(HttpMethod.{}, url) {{ Content = content }};\n".format(method.upper())
                code += "            HttpResponseMessage response = await client.SendAsync(request);\n"
        else:
            method = request.endpoint.method.value.title()
            if method == "Get":
                code += "            HttpResponseMessage response = await client.GetAsync(url);\n"
            elif method == "Delete":
                code += "            HttpResponseMessage response = await client.DeleteAsync(url);\n"
            else:
                code += f"            HttpResponseMessage response = await client.{method}Async(url);\n"
        
        code += "\n            string responseContent = await response.Content.ReadAsStringAsync();\n"
        code += "            Console.WriteLine($\"Status: {response.StatusCode}\");\n"
        code += "            Console.WriteLine($\"Response: {responseContent}\");\n"
        
        if include_error_handling:
            code += "        }\n"
            code += "        catch (Exception e)\n"
            code += "        {\n"
            code += "            Console.WriteLine($\"Request failed: {e.Message}\");\n"
            code += "        }\n"
        
        code += "    }\n"
        code += "}\n"
        
        return code
    
    def _generate_php_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate PHP code using cURL."""
        
        code = "<?php\n\n"
        
        base_url = "https://api.llmgateway.com"
        code += f"$baseUrl = '{base_url}';\n"
        code += f"$endpoint = '{request.endpoint.path}';\n"
        code += "$url = $baseUrl . $endpoint;\n\n"
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        code += "$headers = [\n"
        for key, value in headers.items():
            code += f"    '{key}: {value}',\n"
        code += "];\n\n"
        
        # cURL setup
        code += "$ch = curl_init();\n"
        code += "curl_setopt($ch, CURLOPT_URL, $url);\n"
        code += "curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);\n"
        code += "curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);\n"
        code += f"curl_setopt($ch, CURLOPT_CUSTOMREQUEST, '{request.endpoint.method.value}');\n"
        
        if request.body:
            body_json = json.dumps(request.body)
            code += f"curl_setopt($ch, CURLOPT_POSTFIELDS, '{body_json}');\n"
        
        code += "\n$response = curl_exec($ch);\n"
        
        if include_error_handling:
            code += "\nif (curl_errno($ch)) {\n"
            code += "    echo 'cURL error: ' . curl_error($ch);\n"
            code += "} else {\n"
            code += "    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);\n"
            code += "    echo \"HTTP Status: $httpCode\\n\";\n"
            code += "    echo \"Response: $response\\n\";\n"
            code += "}\n"
        else:
            code += "echo $response;\n"
        
        code += "\ncurl_close($ch);\n"
        code += "\n?>"
        
        return code
    
    def _generate_ruby_code(
        self, 
        request: PlaygroundRequest, 
        include_auth: bool, 
        include_error_handling: bool
    ) -> str:
        """Generate Ruby code using Net::HTTP."""
        
        code = "require 'net/http'\n"
        code += "require 'json'\n"
        code += "require 'uri'\n\n"
        
        base_url = "https://api.llmgateway.com"
        code += f"base_url = '{base_url}'\n"
        code += f"endpoint = '{request.endpoint.path}'\n"
        code += "url = URI(base_url + endpoint)\n\n"
        
        # Add query parameters
        if request.query_params:
            code += "# Add query parameters\n"
            params_str = "&".join([f"{k}={v}" for k, v in request.query_params.items()])
            code += f"url.query = '{params_str}'\n\n"
        
        code += "http = Net::HTTP.new(url.host, url.port)\n"
        code += "http.use_ssl = true\n\n"
        
        # Request
        method_class = {
            "GET": "Net::HTTP::Get",
            "POST": "Net::HTTP::Post", 
            "PUT": "Net::HTTP::Put",
            "DELETE": "Net::HTTP::Delete",
            "PATCH": "Net::HTTP::Patch"
        }.get(request.endpoint.method.value, "Net::HTTP::Get")
        
        code += f"request = {method_class}.new(url)\n"
        
        # Headers
        headers = request.headers.copy()
        if include_auth and "Authorization" not in headers:
            api_key = request.auth_config.get("api_key", "your_api_key_here")
            headers["Authorization"] = f"Bearer {api_key}"
        
        for key, value in headers.items():
            code += f"request['{key}'] = '{value}'\n"
        
        # Request body
        if request.body:
            code += f"\nrequest.body = {json.dumps(request.body)}.to_json\n"
        
        code += "\n"
        
        if include_error_handling:
            code += "begin\n  "
            code += "response = http.request(request)\n"
            code += "  puts \"Status: #{response.code}\"\n"
            code += "  puts \"Response: #{response.body}\"\n"
            code += "rescue => e\n"
            code += "  puts \"Request failed: #{e.message}\"\n"
            code += "end\n"
        else:
            code += "response = http.request(request)\n"
            code += "puts response.body\n"
        
        return code
    
    def _infer_typescript_type(self, value: Any) -> str:
        """Infer TypeScript type from Python value."""
        
        if isinstance(value, str):
            return "string"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, list):
            if value:
                element_type = self._infer_typescript_type(value[0])
                return f"{element_type}[]"
            return "any[]"
        elif isinstance(value, dict):
            return "object"
        else:
            return "any"


class RequestBuilder:
    """
    Interactive request builder for API playground.
    
    Provides step-by-step request construction with:
    - Parameter validation
    - Auto-completion
    - Request templates
    - Real-time validation
    """
    
    def __init__(self, api_spec: Dict[str, Any]):
        """
        Initialize the request builder.
        
        Args:
            api_spec: OpenAPI specification for validation
        """
        self.api_spec = api_spec
        self.endpoints = self._parse_endpoints()
    
    def create_request(
        self, 
        endpoint_path: str, 
        method: str,
        **kwargs
    ) -> PlaygroundRequest:
        """
        Create a playground request with validation.
        
        Args:
            endpoint_path: API endpoint path
            method: HTTP method
            **kwargs: Request parameters
            
        Returns:
            PlaygroundRequest: Validated request object
        """
        
        # Find endpoint definition
        endpoint = self._find_endpoint(endpoint_path, method)
        if not endpoint:
            raise ValueError(f"Endpoint not found: {method} {endpoint_path}")
        
        # Extract request components
        headers = kwargs.get("headers", {})
        query_params = kwargs.get("query_params", {})
        body = kwargs.get("body")
        auth_config = kwargs.get("auth_config", {})
        
        # Validate request
        validation_errors = self._validate_request(endpoint, headers, query_params, body)
        if validation_errors:
            raise ValueError(f"Request validation failed: {validation_errors}")
        
        return PlaygroundRequest(
            id=str(uuid.uuid4()),
            endpoint=endpoint,
            headers=headers,
            query_params=query_params,
            body=body,
            auth_config=auth_config
        )
    
    def get_request_template(self, endpoint_path: str, method: str) -> Dict[str, Any]:
        """Get a request template for an endpoint."""
        
        endpoint = self._find_endpoint(endpoint_path, method)
        if not endpoint:
            raise ValueError(f"Endpoint not found: {method} {endpoint_path}")
        
        template = {
            "endpoint": endpoint_path,
            "method": method,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer your_api_key_here"
            },
            "query_params": {},
            "body": None
        }
        
        # Add parameter templates based on endpoint definition
        if endpoint.parameters:
            for param_name, param_info in endpoint.parameters.items():
                if param_info.get("in") == "query":
                    template["query_params"][param_name] = param_info.get("example", "")
        
        if endpoint.request_body:
            template["body"] = endpoint.request_body.get("example", {})
        
        return template
    
    def validate_auth_config(self, auth_config: Dict[str, str]) -> List[str]:
        """Validate authentication configuration."""
        
        errors = []
        
        if not auth_config.get("api_key"):
            errors.append("API key is required")
        
        # Add more auth validation as needed
        
        return errors
    
    def _parse_endpoints(self) -> List[APIEndpoint]:
        """Parse endpoints from API specification."""
        
        endpoints = []
        
        if not self.api_spec or "paths" not in self.api_spec:
            return endpoints
        
        for path, methods in self.api_spec["paths"].items():
            for method_name, method_info in methods.items():
                if method_name.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = APIEndpoint(
                        path=path,
                        method=HTTPMethod(method_name.upper()),
                        name=method_info.get("summary", f"{method_name.upper()} {path}"),
                        description=method_info.get("description", ""),
                        parameters=method_info.get("parameters", {}),
                        request_body=method_info.get("requestBody", {}),
                        auth_required=True
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _find_endpoint(self, path: str, method: str) -> Optional[APIEndpoint]:
        """Find endpoint by path and method."""
        
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method.value == method.upper():
                return endpoint
        
        return None
    
    def _validate_request(
        self, 
        endpoint: APIEndpoint, 
        headers: Dict[str, str],
        query_params: Dict[str, Any],
        body: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Validate request against endpoint definition."""
        
        errors = []
        
        # Validate required parameters
        for param_name, param_info in endpoint.parameters.items():
            if param_info.get("required", False):
                if param_info.get("in") == "query" and param_name not in query_params:
                    errors.append(f"Missing required query parameter: {param_name}")
        
        # Validate request body if required
        if endpoint.request_body and body is None:
            errors.append("Request body is required for this endpoint")
        
        # Validate authentication
        if endpoint.auth_required and "Authorization" not in headers:
            errors.append("Authorization header is required")
        
        return errors


class APIPlaygroundEngine:
    """
    Complete API playground engine with enterprise features.
    
    Provides:
    - Interactive API testing
    - Real-time request/response visualization
    - Code generation for multiple languages
    - Request history and sharing
    - Performance monitoring
    """
    
    def __init__(self, base_url: str, api_spec: Dict[str, Any]):
        """
        Initialize the API playground engine.
        
        Args:
            base_url: Base URL for API requests
            api_spec: OpenAPI specification
        """
        self.base_url = base_url
        self.api_spec = api_spec
        self.code_generator = CodeGenerator()
        self.request_builder = RequestBuilder(api_spec)
        self.request_history: List[PlaygroundRequest] = []
        self.response_history: List[PlaygroundResponse] = []
    
    async def execute_request(self, request: PlaygroundRequest) -> PlaygroundResponse:
        """
        Execute API request and return response.
        
        Args:
            request: Playground request to execute
            
        Returns:
            PlaygroundResponse: API response with timing
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Build full URL
            url = self.base_url + request.endpoint.path
            
            # Add query parameters
            if request.query_params:
                params = "&".join([f"{k}={v}" for k, v in request.query_params.items()])
                url += f"?{params}"
            
            # Prepare request
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                kwargs = {
                    "method": request.endpoint.method.value,
                    "url": url,
                    "headers": request.headers
                }
                
                if request.body:
                    kwargs["json"] = request.body
                
                async with session.request(**kwargs) as response:
                    response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    
                    # Parse response
                    try:
                        response_body = await response.json()
                    except:
                        response_body = await response.text()
                    
                    # Create response object
                    playground_response = PlaygroundResponse(
                        id=str(uuid.uuid4()),
                        request_id=request.id,
                        status_code=response.status,
                        headers=dict(response.headers),
                        body=response_body,
                        response_time_ms=response_time_ms
                    )
                    
                    # Store in history
                    self.request_history.append(request)
                    self.response_history.append(playground_response)
                    
                    return playground_response
                    
        except Exception as e:
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            error_response = PlaygroundResponse(
                id=str(uuid.uuid4()),
                request_id=request.id,
                status_code=0,
                headers={},
                body=None,
                response_time_ms=response_time_ms,
                error_message=str(e)
            )
            
            self.response_history.append(error_response)
            return error_response
    
    def generate_code_sample(
        self, 
        request: PlaygroundRequest, 
        language: CodeLanguage,
        options: Dict[str, bool] = None
    ) -> str:
        """
        Generate code sample for request.
        
        Args:
            request: Request to generate code for
            language: Target programming language
            options: Code generation options
            
        Returns:
            str: Generated code
        """
        
        if options is None:
            options = {"include_auth": True, "include_error_handling": True}
        
        return self.code_generator.generate_code(
            request, 
            language,
            options.get("include_auth", True),
            options.get("include_error_handling", True)
        )
    
    def get_request_template(self, endpoint_path: str, method: str) -> Dict[str, Any]:
        """Get request template for endpoint."""
        return self.request_builder.get_request_template(endpoint_path, method)
    
    def get_available_endpoints(self) -> List[Dict[str, Any]]:
        """Get list of available API endpoints."""
        
        return [
            {
                "path": endpoint.path,
                "method": endpoint.method.value,
                "name": endpoint.name,
                "description": endpoint.description,
                "auth_required": endpoint.auth_required
            }
            for endpoint in self.request_builder.endpoints
        ]
    
    def get_request_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get request history with responses."""
        
        history = []
        
        for request in self.request_history[-limit:]:
            # Find corresponding response
            response = next(
                (r for r in self.response_history if r.request_id == request.id),
                None
            )
            
            history.append({
                "request": asdict(request),
                "response": asdict(response) if response else None
            })
        
        return history
    
    def clear_history(self):
        """Clear request and response history."""
        self.request_history.clear()
        self.response_history.clear()
    
    def export_request_collection(self, format: str = "json") -> str:
        """Export request collection for sharing."""
        
        collection = {
            "name": "API Playground Collection",
            "timestamp": datetime.utcnow().isoformat(),
            "requests": [asdict(req) for req in self.request_history]
        }
        
        if format.lower() == "json":
            return json.dumps(collection, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_request_collection(self, data: str, format: str = "json"):
        """Import request collection."""
        
        if format.lower() == "json":
            collection = json.loads(data)
            
            for req_data in collection.get("requests", []):
                # Reconstruct request object
                endpoint_data = req_data["endpoint"]
                endpoint = APIEndpoint(**endpoint_data)
                
                request = PlaygroundRequest(
                    id=req_data["id"],
                    endpoint=endpoint,
                    headers=req_data["headers"],
                    query_params=req_data["query_params"],
                    body=req_data["body"],
                    auth_config=req_data["auth_config"],
                    timestamp=datetime.fromisoformat(req_data["timestamp"])
                )
                
                self.request_history.append(request)
        else:
            raise ValueError(f"Unsupported import format: {format}")