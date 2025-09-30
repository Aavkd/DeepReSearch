# n8n Environment Variable Setup Guide

This guide explains how to properly configure n8n to use environment variables from your `.env` file.

## How n8n Uses Environment Variables

n8n can access environment variables in two ways:
1. Through expressions in node parameters: `{{$env('VAR_NAME')}}` (for HTTP Request nodes and other node types)
2. Through the `process.env` object in Function nodes: `process.env.VAR_NAME`

## Setting Up Environment Variables in n8n Nodes

### For HTTP Request Nodes with API Keys

1. Open the HTTP Request node
2. In the "Authentication" section, select the appropriate method
3. For API keys, instead of entering the key directly, use:
   ```
   {{$env('TAVILY_API_KEY')}}
   {{$env('FIRECRAWL_API_KEY')}}
   {{$env('OPENROUTER_API_KEY')}}
   ```

### For Bearer Token Authentication (OpenRouter)

1. In the HTTP Request node settings, set "Authentication" to "Bearer Token"
2. In the "Token" field, enter:
   ```
   {{$env('OPENROUTER_API_KEY')}}
   ```

### In Function Nodes

You can access environment variables in Function nodes using the `process.env` object:
```javascript
const apiKey = process.env.TAVILY_API_KEY;
const model = process.env.OPENROUTER_MODEL;
```

## Testing Environment Variable Access

We've provided a test workflow that you can import to verify that n8n can access your environment variables:

1. Import the `test_n8n_env.json` workflow into n8n
2. Activate the workflow
3. Send a GET request to:
   ```
   http://localhost:5678/webhook/test-env
   ```
4. You should see a response showing which environment variables are set

## Common Issues and Solutions

### Environment Variables Not Available in n8n

1. **Check that the `.env` file is properly referenced in `docker-compose.yml`**:
   ```yaml
   env_file: [.env]
   ```

2. **Restart the services after updating the `.env` file**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Verify the environment variables are loaded**:
   ```bash
   docker-compose exec n8n printenv | grep API_KEY
   ```

### Expression Syntax Errors

Make sure you're using the correct syntax:
- `{{$env('VAR_NAME')}}` for HTTP Request nodes and other node types
- `process.env.VAR_NAME` for Function nodes

## Best Practices

1. **Never hardcode API keys** in your workflow nodes
2. **Always use environment variables** for sensitive information
3. **Restart n8n services** after updating environment variables
4. **Use the test workflow** to verify your setup
5. **Mask sensitive information** in logs and error messages

## Security Considerations

1. Environment variables are accessible to all workflows in n8n
2. Be careful when sharing workflow exports - they may contain references to environment variables
3. Use n8n's credential encryption for additional security
4. Regularly rotate your API keys