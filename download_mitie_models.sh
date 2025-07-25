#!/bin/bash

# MITIE Models Download Script
# Downloads and extracts Spanish MITIE models for Named Entity Recognition

set -e  # Exit on any error

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

# Configuration
MITIE_URL="https://github.com/mit-nlp/MITIE/releases/download/v0.4/MITIE-models-v0.2-Spanish.zip"
MITIE_ZIP="MITIE-models-Spanish.zip"
MITIE_DIR="MITIE-models"
EXPECTED_SIZE=473000000  # ~451MB in bytes

echo "🚀 MITIE Spanish Models Download Script"
echo "======================================"
echo ""

# Check if models already exist
if [ -d "$MITIE_DIR/spanish" ] && [ -f "$MITIE_DIR/spanish/ner_model.dat" ]; then
    print_warning "MITIE Spanish models already exist in $MITIE_DIR/spanish/"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Skipping download. Existing models will be used."
        exit 0
    fi
    print_status "Removing existing models..."
    rm -rf "$MITIE_DIR"
fi

# Check for required tools
if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
    print_error "Neither curl nor wget is available. Please install one of them."
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    print_error "unzip is not available. Please install unzip."
    exit 1
fi

# Determine download tool
if command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -L -o"
    print_status "Using curl for download"
else
    DOWNLOAD_CMD="wget -O"
    print_status "Using wget for download"
fi

# Download MITIE models
print_status "Downloading MITIE Spanish models (~451MB)..."
print_status "This may take several minutes depending on your internet connection..."

if [[ $DOWNLOAD_CMD == curl* ]]; then
    curl -L --progress-bar -o "$MITIE_ZIP" "$MITIE_URL"
else
    wget --progress=bar:force -O "$MITIE_ZIP" "$MITIE_URL"
fi

# Verify download
if [ ! -f "$MITIE_ZIP" ]; then
    print_error "Download failed. File $MITIE_ZIP not found."
    exit 1
fi

# Check file size (approximate)
FILE_SIZE=$(stat -f%z "$MITIE_ZIP" 2>/dev/null || stat -c%s "$MITIE_ZIP" 2>/dev/null || echo "0")
if [ "$FILE_SIZE" -lt 400000000 ]; then  # Less than ~380MB indicates incomplete download
    print_error "Downloaded file appears to be incomplete (size: $FILE_SIZE bytes)"
    print_error "Expected size: ~451MB (473000000 bytes)"
    rm -f "$MITIE_ZIP"
    exit 1
fi

print_success "Download completed successfully (size: $FILE_SIZE bytes)"

# Extract models
print_status "Extracting MITIE models..."

# Create directory if it doesn't exist
mkdir -p "$MITIE_DIR"

# Extract the zip file
unzip -q "$MITIE_ZIP" -d "$MITIE_DIR"

# Check extraction success
if [ ! -f "$MITIE_DIR/spanish/ner_model.dat" ]; then
    print_error "Extraction failed. Spanish NER model not found."
    print_error "Expected file: $MITIE_DIR/spanish/ner_model.dat"
    exit 1
fi

print_success "MITIE models extracted successfully"

# Display extracted contents
print_status "Extracted model files:"
find "$MITIE_DIR" -name "*.dat" -type f | while read -r file; do
    SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
    echo "  - $file ($(echo $SIZE | awk '{printf "%.1fMB", $1/1024/1024}'))"
done

# Clean up downloaded zip file
print_status "Cleaning up downloaded archive..."
rm -f "$MITIE_ZIP"

# Set appropriate permissions
chmod -R 644 "$MITIE_DIR"/*.dat 2>/dev/null || true
chmod 755 "$MITIE_DIR" 2>/dev/null || true
chmod 755 "$MITIE_DIR/spanish" 2>/dev/null || true

print_success "MITIE Spanish models are ready!"
echo ""
echo "📋 Next steps:"
echo "1. The models are now installed in: $MITIE_DIR/spanish/"
echo "2. You can test MITIE backend with:"
echo "   python -m src.cli --backend mitie \"Juan vive en Madrid y trabaja en Google España.\""
echo "3. Or start the web server:"
echo "   python -m src.web_server"
echo ""
echo "💡 Note: MITIE is now the default backend. Use --backend spacy to use spaCy instead."