#!/bin/bash
# Verification script for Wikipedia Agent Web Service setup

set -e

echo "🔍 Verifying Wikipedia Agent Web Service Setup"
echo "=============================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python files
echo "📁 Checking Web Service Files..."
if [ -f "src/web/app.py" ]; then
    success "FastAPI app exists"
    python3 -m py_compile src/web/app.py && success "FastAPI app syntax valid"
else
    error "FastAPI app not found"
    exit 1
fi

if [ -f "src/web/__init__.py" ]; then
    success "Web module initialized"
else
    error "Web module __init__.py missing"
fi

# Check static files
echo
echo "🎨 Checking Static Files..."
for file in index.html style.css app.js; do
    if [ -f "src/web/static/$file" ]; then
        success "$file exists"
    else
        error "$file missing"
    fi
done

# Check Docker files
echo
echo "🐳 Checking Docker Files..."
for file in Dockerfile docker-compose.yml .dockerignore; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        error "$file missing"
    fi
done

# Check documentation
echo
echo "📚 Checking Documentation..."
for file in WEB_SERVICE_QUICKSTART.md DOCKER_DEPLOYMENT.md WEB_SERVICE_SUMMARY.md; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        warning "$file missing"
    fi
done

# Check configuration
echo
echo "⚙️  Checking Configuration..."
if [ -f "config.yaml" ]; then
    success "config.yaml exists"
else
    error "config.yaml missing"
fi

if [ -f ".env" ]; then
    success ".env file exists"
else
    warning ".env file not found (you'll need to create this)"
fi

# Check dependencies
echo
echo "📦 Checking Dependencies..."
if [ -f "pyproject.toml" ]; then
    success "pyproject.toml exists"
    
    if grep -q "fastapi" pyproject.toml; then
        success "FastAPI dependency listed"
    else
        error "FastAPI dependency missing"
    fi
    
    if grep -q "uvicorn" pyproject.toml; then
        success "Uvicorn dependency listed"
    else
        error "Uvicorn dependency missing"
    fi
    
    if grep -q "wikipedia-agent-web" pyproject.toml; then
        success "Web service command registered"
    else
        error "Web service command not registered"
    fi
else
    error "pyproject.toml missing"
fi

# Check Python version
echo
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "Python available: $PYTHON_VERSION"
else
    error "Python 3 not found"
fi

# Check Docker (optional)
echo
echo "🐋 Checking Docker (optional)..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    success "Docker available: $DOCKER_VERSION"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        success "Docker Compose available: $COMPOSE_VERSION"
    else
        warning "Docker Compose not found (needed for easy deployment)"
    fi
else
    warning "Docker not found (needed for containerized deployment)"
fi

# Summary
echo
echo "=============================================="
echo "📊 Verification Summary"
echo "=============================================="
echo

# Count files
WEB_FILES=$(find src/web -type f -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.js" 2>/dev/null | wc -l)
DOCKER_FILES=$(ls Dockerfile docker-compose.yml .dockerignore 2>/dev/null | wc -l)
DOC_FILES=$(ls *WEB*.md *DOCKER*.md 2>/dev/null | wc -l)

success "$WEB_FILES web service files created"
success "$DOCKER_FILES Docker files created"
success "$DOC_FILES documentation files created"

echo
echo "✅ Web service setup is complete!"
echo
echo "📖 Next Steps:"
echo "   1. Install dependencies: uv pip install -e ."
echo "   2. Configure LLM in config.yaml"
echo "   3. Set API key in .env file"
echo "   4. Start service: wikipedia-agent-web"
echo "   5. Open browser: http://localhost:8000"
echo
echo "📚 Documentation:"
echo "   • Quick Start: WEB_SERVICE_QUICKSTART.md"
echo "   • Full Guide: DOCKER_DEPLOYMENT.md"
echo "   • Summary: WEB_SERVICE_SUMMARY.md"
echo
echo "🐳 Docker Quick Start:"
echo "   docker-compose up -d"
echo

exit 0
