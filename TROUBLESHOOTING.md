# Troubleshooting Guide

This guide covers common issues and their solutions when setting up and running the Local Perplexity Engine.

## Common Issues and Solutions

### 1. Webhook Returns 404 Error

**Problem**: When testing the API, you receive a 404 error with the message "This webhook is not registered for POST requests."

**Solutions**:
1. **Check if the workflow is imported**: 
   - Open n8n at http://localhost:5678
   - Go to the "Workflows" section
   - Verify that "Local Perplexity RAG" workflow exists

2. **Check if the workflow is activated**:
   - In the workflow editor, look for the "Active" toggle in the top right
   - If it's off (gray), click it to activate the workflow
   - An active workflow will have a green toggle

3. **Verify webhook configuration**:
   - Open the "Webhook" node in the workflow
   - Check that the path is set to "api/search"
   - Check that the method is set to "POST"
   - Check that "Respond" is set to "When last node finishes"

4. **Restart n8n**:
   - Stop the services: `docker-compose down`
   - Start the services: `docker-compose up -d`
   - Wait for services to initialize and try again

### 2. Connection Refused Error

**Problem**: The test script cannot connect to n8n with a "Connection refused" error.

**Solutions**:
1. **Check if Docker services are running**:
   ```bash
   docker-compose ps
   ```
   All services should show "Up" status.

2. **Start the services if they're not running**:
   ```bash
   docker-compose up -d
   ```

3. **Check for port conflicts**:
   - Verify that ports 5678, 6379, 5432, and 11434 are not being used by other applications
   - If there are conflicts, you can change the ports in `docker-compose.yml` and `.env`

### 3. API Keys Not Working

**Problem**: Search or LLM nodes are failing with authentication errors.

**Solutions**:
1. **Verify API keys in n8n credentials**:
   - Open any HTTP Request node that requires an API key
   - Click on the credential selector
   - Check that the API key is correctly entered
   - If not, update the credential with the correct key

2. **Configure n8n to use environment variables**:
   - For each HTTP Request node that requires an API key:
     1. Click on the node to open its settings
     2. In the "Authentication" section, select the appropriate authentication method
     3. For API keys, instead of entering the key directly, use the expression `{{$env('ENV_VAR_NAME')}}`
     4. For example, for Tavily API key, use `{{$env('TAVILY_API_KEY')}}`
     5. For OpenRouter API key, use `{{$env('OPENROUTER_API_KEY')}}`
     6. For Firecrawl API key, use `{{$env('FIRECRAWL_API_KEY')}}`
   - For Bearer Token authentication (OpenRouter):
     1. In the HTTP Request node settings, set "Authentication" to "Bearer Token"
     2. In the "Token" field, enter `{{$env('OPENROUTER_API_KEY')}}`
   - See our detailed [n8n Environment Setup Guide](N8N_ENV_SETUP.md) for more information

3. **Check environment variables**:
   - Verify that your `.env` file contains the correct API keys
   - Ensure there are no extra spaces or quotes around the keys
   - Restart services after updating the `.env` file:
     ```bash
     docker-compose down
     docker-compose up -d
     ```

4. **Verify environment variables are loaded**:
   - Check that the `.env` file is properly referenced in `docker-compose.yml`
   - You can verify the environment variables are loaded by running:
     ```bash
     docker-compose exec n8n printenv | grep API_KEY
     ```

5. **Test environment variable access**:
   - Import the `test_n8n_env.json` workflow to verify that n8n can access your environment variables
   - Activate the workflow and send a GET request to `http://localhost:5678/webhook/test-env`

### 4. Ollama Model Not Found

**Problem**: Ollama-related nodes fail with "model not found" errors.

**Solutions**:
1. **Pull the required model**:
   ```bash
   docker exec -it ollama ollama pull qwen2.5:14b-instruct
   ```

2. **Check model name in environment variables**:
   - Verify that `OLLAMA_MODEL` in `.env` matches the model you pulled
   - The default is `qwen2.5:14b-instruct`

3. **Test Ollama directly**:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   This should list the available models.

### 5. Slow Performance

**Problem**: The search engine takes too long to respond.

**Solutions**:
1. **Check network connectivity**:
   - Verify that you can access external APIs (Tavily, Firecrawl, etc.)
   - Test with a simple curl command:
     ```bash
     curl -X POST https://api.tavily.com/search \
       -H "Content-Type: application/json" \
       -d '{"api_key": "YOUR_API_KEY", "query": "test"}'
     ```

2. **Adjust maxResults parameter**:
   - Reduce the `maxResults` value in your request to decrease processing time
   - Start with 3-5 results instead of the default 6

3. **Check resource usage**:
   ```bash
   docker stats
   ```
   This will show CPU and memory usage for each container.

### 6. JSON Parsing Errors

**Problem**: The response contains invalid JSON or unexpected format.

**Solutions**:
1. **Check LLM responses**:
   - In n8n, enable "Save Output" for the Synthesis LLM node
   - Check the execution log to see the raw LLM response
   - Verify that the LLM is returning valid JSON

2. **Verify prompt formatting**:
   - Check the "Synthesis LLM" node configuration
   - Ensure the system prompt clearly specifies JSON output format

3. **Test with a simpler query**:
   - Try a more straightforward query to see if the issue persists

## Debugging Commands

### Check service status
```bash
docker-compose ps
```

### View n8n logs
```bash
docker-compose logs n8n
```

### View all logs
```bash
docker-compose logs
```

### Check resource usage
```bash
docker stats
```

### Test Ollama
```bash
curl http://localhost:11434/api/tags
```

### Test Redis connection
```bash
docker exec -it redis redis-cli ping
```

### Test PostgreSQL connection
```bash
docker exec -it postgres psql -U perplex -d perplex -c "SELECT version();"
```

### Verify environment variables in n8n container
```bash
docker-compose exec n8n printenv | grep -E "(API|KEY)"
```

## Need More Help?

If you're still experiencing issues:

1. **Check the n8n community forum**: https://community.n8n.io/
2. **Review the n8n documentation**: https://docs.n8n.io/
3. **File an issue on GitHub** if you believe you've found a bug in this project

When seeking help, include:
- The exact error message
- Relevant log output
- Your environment configuration (with sensitive data redacted)
- Steps you've already tried