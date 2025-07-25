#!/bin/bash

# Docker Build Script for Spanish NER Service
# Supports building with different backend configurations

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'  
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuration
IMAGE_NAME="spanish-ner"
TAG="latest"

echo "🐳 Spanish NER Service - Docker Build"
echo "====================================="
echo ""

# Parse command line arguments
BACKEND="mitie"  # Default backend
NO_CACHE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend BACKEND   Set default backend (mitie|spacy) [default: mitie]"
            echo "  --tag TAG          Set image tag [default: latest]" 
            echo "  --no-cache         Build without using cache"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Build with MITIE backend"
            echo "  $0 --backend spacy           # Build with spaCy backend"
            echo "  $0 --tag v1.0 --no-cache    # Build v1.0 tag without cache"
            exit 0
            ;;
        *)
            print_warning "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate backend
if [[ "$BACKEND" != "mitie" && "$BACKEND" != "spacy" ]]; then
    print_warning "Invalid backend: $BACKEND. Must be 'mitie' or 'spacy'"
    exit 1
fi

print_status "Building Docker image: $IMAGE_NAME:$TAG"
print_status "Default backend: $BACKEND"

# Build Docker image
print_status "Starting Docker build..."

docker build $NO_CACHE \
    --build-arg DEFAULT_BACKEND="$BACKEND" \
    -t "$IMAGE_NAME:$TAG" \
    -t "$IMAGE_NAME:$BACKEND-$TAG" \
    .

print_success "Docker image built successfully!"
echo ""
echo "📋 Available images:"
docker images | grep "$IMAGE_NAME" | head -5

echo ""
echo "🚀 Quick start commands:"
echo ""
echo "# Run with default configuration:"
echo "docker run -p 8000:8000 $IMAGE_NAME:$TAG"
echo ""
echo "# Run with custom backend:"
echo "docker run -p 8000:8000 -e NER_BACKEND=spacy $IMAGE_NAME:$TAG"
echo ""
echo "# Run with docker-compose:"
echo "docker-compose up"
echo ""
echo "# Access the API:"
echo "curl http://localhost:8000/health"
echo "curl -X POST http://localhost:8000/ner -H 'Content-Type: application/json' -d '{\"text\": \"Juan vive en Madrid\"}'"