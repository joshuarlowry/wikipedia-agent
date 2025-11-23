# Web Service Quick Start Guide

Get the Wikipedia Research Agent web service running in under 5 minutes!

## 🎯 Quick Start Options

### Option 1: Docker (Easiest - Recommended)

**Prerequisites:** Docker and Docker Compose installed

```bash
# 1. Configure your LLM provider in config.yaml
# (Already set up by default to use OpenRouter)

# 2. Add your API key to .env
echo "OPENROUTER_API_KEY=your_key_here" > .env

# 3. Start the service
docker-compose up -d

# 4. Open your browser
open http://localhost:8000
```

That's it! The web UI is ready to use.

### Option 2: Local Python Installation

**Prerequisites:** Python 3.10+, uv (or pip)

```bash
# 1. Install dependencies
uv pip install -e .
# OR: pip install -e .

# 2. Configure your LLM provider in config.yaml
# (Already set up by default to use OpenRouter)

# 3. Add your API key to .env
echo "OPENROUTER_API_KEY=your_key_here" > .env

# 4. Start the web service
wikipedia-agent-web

# 5. Open your browser
open http://localhost:8000
```

## 📝 Configuration

### Step 1: Choose Your LLM Provider

Edit `config.yaml`:

**For OpenRouter (Cloud - Recommended for getting started):**
```yaml
llm:
  provider: "openrouter"
```

**For Ollama (Local - No API key needed):**
```yaml
llm:
  provider: "ollama"
```

### Step 2: Set Up Credentials

**For OpenRouter:**
1. Get an API key from https://openrouter.ai
2. Add to `.env`:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

**For Ollama:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull mistral:latest`
3. No API key needed!

If using Docker with Ollama, uncomment the Ollama service in `docker-compose.yml`.

## 🌐 Using the Web Interface

### Basic Usage

1. **Open** http://localhost:8000
2. **Type** your question in the text area
3. **Select** output format:
   - **MLA Format**: Narrative response with citations
   - **JSON Format**: Structured data with facts and sources
4. **Click** "Ask Question"
5. **Watch** the response stream in real-time!

### Example Questions

- "What is quantum computing?"
- "Explain the history of artificial intelligence"
- "How does photosynthesis work?"
- "What caused World War II?"

### Output Formats

**MLA Format** - For readable, cited content:
```
Quantum computing is a revolutionary approach...

Works Cited
"Quantum Computing." Wikipedia, ...
```

**JSON Format** - For programmatic use:
```json
{
  "query": "What is quantum computing?",
  "sources": [...],
  "facts": [...],
  "summary": "..."
}
```

## 🔌 Using the REST API

### Check Service Health

```bash
curl http://localhost:8000/health
```

### Query the Agent

**Streaming (Real-time):**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is quantum computing?",
    "stream": true
  }'
```

**Non-Streaming:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is quantum computing?",
    "stream": false,
    "output_format": "mla"
  }'
```

**Get JSON Format:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "stream": false,
    "output_format": "json"
  }'
```

### API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Commands

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart after config changes
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# View status
docker-compose ps
```

## 🔧 Troubleshooting

### Service won't start

**Check logs:**
```bash
docker-compose logs wikipedia-agent-web
```

**Common issues:**
- Missing API key in `.env`
- Invalid `config.yaml` format
- Port 8000 already in use

**Solutions:**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use port 8080 instead

# Or use environment variable
PORT=8080 wikipedia-agent-web
```

### Connection Refused

**Check if service is running:**
```bash
docker-compose ps
# OR
curl http://localhost:8000/health
```

### Out of Memory (when using Ollama)

**Increase Docker memory:**
- Docker Desktop: Settings → Resources → Memory → 8GB+
- Or use a smaller model: `ollama pull llama3.2:3b`

### Slow Responses

**Try a faster model:**

For OpenRouter in `config.yaml`:
```yaml
model: "meta-llama/llama-3.3-70b-instruct"  # Fast and cheap
```

For Ollama:
```yaml
model: "llama3.2"  # Lightweight
```

## 🚀 Next Steps

### Customize the UI

Edit the static files:
- `src/web/static/index.html` - HTML structure
- `src/web/static/style.css` - Styling
- `src/web/static/app.js` - JavaScript logic

### Add Authentication

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for production deployment with nginx and authentication.

### Integrate with Your App

```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={"query": "What is AI?", "stream": False}
)
print(response.json()["response"])
```

```javascript
const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'What is AI?', stream: false})
});
const data = await response.json();
console.log(data.response);
```

## 📚 Additional Documentation

- **Full Deployment Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Main Documentation**: [README.md](README.md)
- **API Reference**: http://localhost:8000/docs (when running)

## 💡 Tips

1. **Start with OpenRouter** - Easiest to get running, no local setup
2. **Enable streaming** - Better UX, see responses as they generate
3. **Use JSON format** - For programmatic integrations
4. **Try different models** - Balance speed vs quality based on your needs

## ❓ Need Help?

- Check logs: `docker-compose logs -f`
- Verify config: `cat config.yaml`
- Test health: `curl http://localhost:8000/health`
- Read full docs: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

## 🎉 You're All Set!

The Wikipedia Research Agent web service is now running and ready to answer questions with proper Wikipedia citations!

**Quick Test:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?", "stream": false}'
```

Enjoy researching! 📚🚀
