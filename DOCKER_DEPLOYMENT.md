# Docker Deployment Guide

This guide covers deploying the Wikipedia Research Agent as a web service using Docker.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Configure your LLM provider**

   Edit `config.yaml` to select your LLM provider (Ollama or OpenRouter):

   ```yaml
   llm:
     provider: "openrouter"  # or "ollama"
   ```

2. **Set up API keys (if using OpenRouter)**

   Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Start the service**

   ```bash
   docker-compose up -d
   ```

4. **Access the web UI**

   Open your browser to: http://localhost:8000

   API documentation available at: http://localhost:8000/docs

### Using Docker Only

```bash
# Build the image
docker build -t wikipedia-agent-web .

# Run the container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -e OPENROUTER_API_KEY=your_key_here \
  --name wikipedia-agent-web \
  wikipedia-agent-web
```

## 📋 Configuration

### LLM Providers

#### Option 1: OpenRouter (Cloud)

Easiest option - no local setup required.

```yaml
llm:
  provider: "openrouter"
  openrouter:
    api_key_env: "OPENROUTER_API_KEY"
    model: "meta-llama/llama-3.3-70b-instruct"
```

Set your API key in `.env`:
```bash
OPENROUTER_API_KEY=your_key_here
```

#### Option 2: Ollama (Local)

For local LLM inference. Uncomment the Ollama service in `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
```

Update `config.yaml`:
```yaml
llm:
  provider: "ollama"
  ollama:
    base_url: "http://ollama:11434"
    model: "mistral:latest"
```

Then pull a model:
```bash
docker-compose exec ollama ollama pull mistral:latest
```

## 🌐 Web Interface

The web UI provides:

- **Clean, modern interface** for asking questions
- **Real-time streaming responses** from the LLM
- **Two output formats**:
  - **MLA Format**: Narrative responses with proper citations
  - **JSON Format**: Structured data with sources and facts
- **Responsive design** that works on desktop and mobile

### Example Usage

1. Open http://localhost:8000
2. Type a question: "What is quantum computing?"
3. Select output format (MLA or JSON)
4. Click "Ask Question"
5. Watch the response stream in real-time!

## 🔌 REST API

### Endpoints

#### `POST /api/query`

Query the agent with a question.

**Request:**
```json
{
  "query": "What is quantum computing?",
  "stream": true,
  "output_format": "mla"
}
```

**Response (streaming):**
```
data: {"chunk": "Quantum computing is..."}
data: {"chunk": " a revolutionary..."}
data: {"done": true}
```

**Response (non-streaming):**
```json
{
  "response": "Quantum computing is...\n\nWorks Cited\n...",
  "output_format": "mla"
}
```

#### `GET /health`

Check service health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "provider": "openrouter",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "ready": true
}
```

#### `GET /api/config`

Get current configuration (sanitized).

**Response:**
```json
{
  "provider": "openrouter",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "output_format": "mla",
  "max_articles": 3,
  "language": "en"
}
```

### API Examples

**Using cURL:**

```bash
# Streaming query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?", "stream": true}'

# Non-streaming query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "stream": false}'

# JSON format
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "stream": false, "output_format": "json"}'
```

**Using Python:**

```python
import requests

# Query the agent
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "What is quantum computing?",
        "stream": False,
        "output_format": "mla"
    }
)

print(response.json()["response"])
```

**Using JavaScript:**

```javascript
// Streaming query
const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        query: 'What is quantum computing?',
        stream: true
    })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    console.log(chunk);
}
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONFIG_PATH` | Path to config file | `/app/config.yaml` |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `PORT` | Port to bind to | `8000` |
| `HOST` | Host to bind to | `0.0.0.0` |

## 📊 Monitoring

### Health Checks

The service includes health checks:

```bash
# Check service health
curl http://localhost:8000/health

# Docker health check status
docker ps --filter name=wikipedia-agent-web
```

### Logs

```bash
# View logs
docker-compose logs -f wikipedia-agent-web

# View Ollama logs (if using)
docker-compose logs -f ollama
```

## 🔒 Security Considerations

1. **API Keys**: Store API keys in `.env` file, never commit them
2. **Network**: Use a reverse proxy (nginx, Caddy) for production
3. **HTTPS**: Enable HTTPS in production using Let's Encrypt
4. **Rate Limiting**: Consider adding rate limiting for public APIs
5. **CORS**: Configure CORS properly for your domain

## 🚢 Production Deployment

### With Nginx Reverse Proxy

1. Update `docker-compose.yml` to not expose port directly:
   ```yaml
   wikipedia-agent-web:
     expose:
       - "8000"
   ```

2. Add nginx service:
   ```yaml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
     depends_on:
       - wikipedia-agent-web
   ```

### Environment-Specific Configs

Create different config files:

```bash
# Development
docker-compose -f docker-compose.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 🛠 Troubleshooting

### Service won't start

1. Check logs: `docker-compose logs wikipedia-agent-web`
2. Verify config.yaml is valid
3. Ensure API keys are set correctly

### Connection refused

1. Check service is running: `docker ps`
2. Verify port 8000 is not already in use
3. Check firewall settings

### Ollama model not found

```bash
# Pull the model
docker-compose exec ollama ollama pull mistral:latest

# List available models
docker-compose exec ollama ollama list
```

### Out of memory

Increase Docker memory limits in Docker Desktop settings or add to docker-compose.yml:

```yaml
services:
  wikipedia-agent-web:
    deploy:
      resources:
        limits:
          memory: 4G
```

## 📦 Building Custom Images

### Build Arguments

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t wikipedia-agent-web:latest \
  .
```

### Multi-Architecture Builds

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-registry/wikipedia-agent-web:latest \
  --push \
  .
```

## 🔄 Updates

### Update the service

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Update Ollama models

```bash
docker-compose exec ollama ollama pull mistral:latest
```

## 💡 Usage Tips

1. **Choose the right model**: 
   - For speed: `llama3.2`, `mistral:latest`
   - For quality: `llama-3.3-70b`, `claude-3.5-sonnet`

2. **Output formats**:
   - Use **MLA** for readable, cited responses
   - Use **JSON** for programmatic access and structured data

3. **Streaming**:
   - Enable streaming for better UX (see responses as they generate)
   - Disable for batch processing or API integrations

4. **Resource usage**:
   - OpenRouter: Pay per request, no local resources
   - Ollama: Free but requires significant RAM/CPU (4-8GB+ RAM)

## 🤝 Integration Examples

### With React/Next.js

```javascript
// components/WikipediaAgent.jsx
export function WikipediaAgent() {
  const [response, setResponse] = useState('');
  
  const query = async (question) => {
    const res = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: question, stream: false})
    });
    const data = await res.json();
    setResponse(data.response);
  };
  
  return <div>{/* your UI */}</div>;
}
```

### With Python (Background Tasks)

```python
import asyncio
import aiohttp

async def query_agent(question):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/query',
            json={'query': question, 'stream': False}
        ) as resp:
            data = await resp.json()
            return data['response']

# Use in async context
response = await query_agent("What is quantum computing?")
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Main README**: [README.md](README.md)
- **Strands Documentation**: https://strandsagents.com/
- **Wikipedia API**: https://wikipedia.readthedocs.io/

## ⚖️ License

Same as main project - see [README.md](README.md)
