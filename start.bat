@echo off
title Perplexity Engine Starter

echo Starting Perplexity Engine services...
docker-compose up -d

echo.
echo Waiting for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo Checking service status...
docker-compose ps

echo.
echo Services started successfully!
echo n8n is available at: http://localhost:5678
echo PostgreSQL is available at: localhost:5432
echo Redis is available at: localhost:6379
echo Ollama is available at: http://localhost:11434

echo.
echo Next steps:
echo 1. Import the workflow at n8n\workflows\local_perplexity_rag.json into n8n
echo 2. Configure your API credentials in n8n
echo 3. Run the test script: python test_search.py
echo 4. Open ui\index.html in your browser for the reference UI

pause