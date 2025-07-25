#!/bin/bash

# Spanish NER Service - Setup Script
# This script sets up a virtual environment and installs dependencies for chosen NER backend

set -e  # Exit on any error

echo "🚀 Setting up Spanish NER Service..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Ask user for backend choice
echo ""
echo "🔧 Choose NER Backend:"
echo "1) spaCy - Fast CNN model, 93MB model"
echo "2) MITIE (default) - High accuracy, 451MB model (requires additional setup)"
echo "3) Both - Install both backends"
echo ""
read -p "Enter your choice (1-3) [2]: " BACKEND_CHOICE
BACKEND_CHOICE=${BACKEND_CHOICE:-2}

case $BACKEND_CHOICE in
    1)
        INSTALL_SPACY=true
        INSTALL_MITIE=false
        print_status "Selected: spaCy backend"
        ;;
    2)
        INSTALL_SPACY=false
        INSTALL_MITIE=true
        print_status "Selected: MITIE backend (default)"
        ;;
    3)
        INSTALL_SPACY=true
        INSTALL_MITIE=true
        print_status "Selected: Both backends"
        ;;
    *)
        print_warning "Invalid choice, defaulting to MITIE"
        INSTALL_SPACY=false
        INSTALL_MITIE=true
        ;;
esac

# Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements based on backend choice
if [ "$INSTALL_SPACY" = true ]; then
    print_status "Installing spaCy dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "spaCy dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
fi

if [ "$INSTALL_MITIE" = true ]; then
    print_status "Installing MITIE dependencies..."
    if [ -f "requirements-mitie.txt" ]; then
        pip install -r requirements-mitie.txt
        print_success "MITIE dependencies installed"
    else
        print_error "requirements-mitie.txt not found"
        exit 1
    fi
fi

# Download models based on backend choice
if [ "$INSTALL_SPACY" = true ]; then
    print_status "Downloading Spanish spaCy models..."
    python -m spacy download es_core_news_md
    python -m spacy download es_core_news_sm || print_warning "Could not download fallback model (es_core_news_sm)"
fi

if [ "$INSTALL_MITIE" = true ]; then
    print_status "Setting up MITIE models..."
    
    # Check if MITIE model directory exists
    if [ ! -d "MITIE-models" ]; then
        print_status "MITIE models not found. Please download manually:"
        echo "1. Download from: https://github.com/mit-nlp/MITIE/releases/download/v0.4/MITIE-models-v0.2-Spanish.zip"
        echo "2. Extract to project directory as 'MITIE-models/'"
        print_warning "MITIE models must be downloaded manually due to size (451MB)"
    else
        print_success "MITIE models directory found"
    fi
fi

print_success "Setup completed!"

echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Test the CLI:"
if [ "$INSTALL_SPACY" = true ] && [ "$INSTALL_MITIE" = true ]; then
    echo "   # Test with spaCy (default):"
    echo "   python -m src.cli \"Juan vive en Madrid y trabaja en Google España.\""
    echo ""
    echo "   # Test with MITIE:"
    echo "   python -m src.cli --backend mitie \"Juan vive en Madrid y trabaja en Google España.\""
    echo ""
    echo "   # Show backend info:"
    echo "   python -m src.cli info"
elif [ "$INSTALL_MITIE" = true ]; then
    echo "   python -m src.cli --backend mitie \"Juan vive en Madrid y trabaja en Google España.\""
else
    echo "   python -m src.cli \"Juan vive en Madrid y trabaja en Google España.\""
fi
echo ""
echo "3. Start the web server:"
echo "   python -m src.web_server"
echo ""
echo "4. Access the API:"
echo "   Documentation: http://localhost:8000/docs"
echo "   Backend info:  http://localhost:8000/backends"
echo ""
echo "5. To deactivate the virtual environment when done:"
echo "   deactivate"