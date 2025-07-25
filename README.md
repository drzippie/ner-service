# Spanish NER Service

A Python application for Named Entity Recognition (NER) in Spanish with configurable backends (spaCy and MITIE). Provides both a command-line interface and a REST API for extracting named entities from Spanish text.

## Features

- **Configurable Backends**: Choose between spaCy (fast, lightweight) or MITIE (high accuracy)
- **Multiple Models**: spaCy's es_core_news_md model or MITIE's Spanish NER model
- **Multiple Interfaces**: Command-line tool and REST API
- **Entity Types**: PERSON, LOCATION, ORGANIZATION, MISC, PLACE
- **Flexible Output**: JSON, table, and simple text formats
- **Fast API**: Built with FastAPI for high performance
- **Interactive Documentation**: Automatic API documentation with Swagger UI

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the Spanish NER Service is using Docker:

1. Clone the repository:
```bash
git clone https://github.com/drzippie/ner-service.git
cd ner-service
```

2. Build and run with Docker:
```bash
# Build the image
./docker-build.sh

# Run with docker-compose (MITIE backend by default)
docker-compose up

# Or run directly
docker run -p 8000:8000 spanish-ner:latest
```

3. Access the API:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Option 2: Automatic Setup

1. Clone the repository:
```bash
git clone https://github.com/drzippie/ner-service.git
cd ner-service
```

2. Run the setup script:

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

The setup script will:
- Create a virtual environment
- Let you choose between spaCy, MITIE, or both backends
- Install the appropriate dependencies
- Download the Spanish NER models
- Provide next steps

### Option 3: Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/drzippie/ner-service.git
cd ner-service
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate.bat
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the Spanish NER model:
```bash
python -m spacy download es_core_news_md
```

## Usage

### Command Line Interface

**Important:** Make sure your virtual environment is activated before running commands:
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
```

Analyze text directly:
```bash
# Using default backend (MITIE)
python -m src.cli "Juan vive en Madrid y trabaja en Google España."

# Using specific backend
python -m src.cli --backend mitie "Juan vive en Madrid y trabaja en Google España."
python -m src.cli --backend spacy "Juan vive en Madrid y trabaja en Google España."
```

Analyze text from file:
```bash
python -m src.cli --file input.txt --format table
```

Save results to file:
```bash
python -m src.cli "María estudió en Barcelona" --output results.json
```

#### CLI Options

- `--file, -f`: Input text file to analyze
- `--output, -o`: Output file for results
- `--format`: Output format (`json`, `table`, `simple`)
- `--backend, -b`: NER backend to use (`spacy` or `mitie`)
- `--quiet, -q`: Suppress informational messages
- `--help`: Show help message

#### Backend Information

Show information about available backends:
```bash
python -m src.cli info
```

### Web API

**Important:** Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
```

Start the server:
```bash
python -m src.web_server
```

The API will be available at `http://localhost:8000`

#### API Endpoints

- **POST /ner**: Analyze text for named entities
- **GET /health**: Check API status with backend info
- **GET /backends**: Get information about all available backends
- **GET /docs**: Interactive API documentation
- **GET /**: API information

#### Example API Usage

```bash
curl -X POST "http://localhost:8000/ner" \
     -H "Content-Type: application/json" \
     -d '{"text": "Juan vive en Madrid y trabaja en Google España."}'
```

Response (array returned directly):
```json
[
  {
    "tag": "PERSON",
    "score": "0.7588",
    "label": "Juan"
  },
  {
    "tag": "LOCATION", 
    "score": "1.2897",
    "label": "Madrid"
  },
  {
    "tag": "LOCATION",
    "score": "0.7335",
    "label": "Google Spain"
  }
]
```

## Backend Options

### MITIE Backend (Default)

- **Model**: Spanish NER model using Structural Support Vector Machines
- **Size**: 451MB
- **Performance**: High accuracy with distributional word embeddings and real confidence scores
- **Technology**: Built on dlib, state-of-the-art techniques
- **Score Filtering**: Only entities with confidence >= 0.5 are returned
- **Installation**: Use `./download_mitie_models.sh` or manual download from [MITIE releases](https://github.com/mit-nlp/MITIE/releases/download/v0.4/MITIE-models-v0.2-Spanish.zip)

### spaCy Backend

- **Primary**: `es_core_news_md` - Spanish CNN model trained on UD Spanish AnCora and WikiNER (89.01% F-score)
- **Fallback**: `es_core_news_sm` - Smaller Spanish model for basic NER tasks
- **Size**: 93MB (md) or 12MB (sm)
- **Performance**: Fast processing, optimized for CPU
- **Score**: Fixed confidence score of 0.95 for all entities
- **Installation**: `python -m spacy download es_core_news_md`

### Backend Selection

- **Environment Variable**: Set `NER_BACKEND=mitie` or `NER_BACKEND=spacy`
- **CLI Flag**: Use `--backend mitie` or `--backend spacy`
- **Default**: MITIE (if not specified)

## Entity Types

The service recognizes the following entity types:

- **PERSON**: Names of people
- **LOCATION**: Geographic locations (cities, countries, etc.)
- **ORGANIZATION**: Companies, institutions, organizations
- **PLACE**: Specific places and venues
- **MISC**: Miscellaneous entities that don't fit other categories

## Output Format

All entities are returned with the following structure:

```json
{
  "tag": "ENTITY_TYPE",
  "score": "0.7588",
  "label": "Entity Name"
}
```

- `tag`: The entity type (PERSON, LOCATION, ORGANIZATION, MISC, PLACE)
- `score`: Confidence score (real scores from MITIE backend, fixed 0.95 for spaCy backend)
- `label`: The actual text of the identified entity

**Important**: 
- All entities are unique - duplicate entities with the same label and tag are automatically filtered out
- **MITIE backend**: Only entities with score >= 0.5 are returned (score filtering)
- **spaCy backend**: All detected entities are returned with fixed score of 0.95

## Virtual Environment Management

### Working with Virtual Environments

**Activate the environment:**
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

**Deactivate when done:**
```bash
deactivate
```

**Verify activation:**
```bash
which python  # Should point to venv/bin/python
pip list      # Should show only project dependencies
```

### Benefits of Virtual Environment

- **Isolation**: Dependencies don't conflict with system packages
- **Reproducibility**: Exact same environment across different machines
- **Clean**: Easy to remove by deleting the `venv` folder
- **Version Control**: `venv/` is ignored in git (see `.gitignore`)

## Development

### Project Structure

```
ner-service/
├── src/
│   ├── __init__.py
│   ├── ner_core.py      # Core NER functionality
│   ├── cli.py           # Command-line interface
│   └── web_server.py    # FastAPI web server
├── requirements.txt     # Dependencies
├── setup.py            # Package configuration
├── __main__.py         # Module entry point
└── README.md           # This file
```

### Running Tests

Install the package in development mode:
```bash
pip install -e .
```

### API Documentation

When running the web server, interactive documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Requirements

### Base Requirements
- Python 3.8+
- FastAPI
- Click
- Uvicorn

### Backend-Specific Requirements

**spaCy Backend:**
- spaCy 3.4+
- Spanish models (es_core_news_md/sm)

**MITIE Backend:**
- MITIE library
- Spanish MITIE model (451MB)
- dlib (included with MITIE)

See `requirements.txt` and `requirements-mitie.txt` for specific versions.

## Docker Deployment

### Building the Docker Image

```bash
# Build with default MITIE backend
./docker-build.sh

# Build with spaCy backend as default
./docker-build.sh --backend spacy

# Build without cache
./docker-build.sh --no-cache --tag v1.0
```

### Running with Docker

```bash
# Using docker-compose (recommended)
docker-compose up

# Run specific backend
docker run -p 8000:8000 -e NER_BACKEND=mitie spanish-ner:latest
docker run -p 8000:8000 -e NER_BACKEND=spacy spanish-ner:latest

# Run spaCy-only service on different port
docker-compose --profile spacy-only up spanish-ner-spacy
```

### Docker Environment Variables

- `NER_BACKEND`: Set backend (`mitie` or `spacy`) [default: `mitie`]
- `API_HOST`: Server host [default: `0.0.0.0`]
- `API_PORT`: Server port [default: `8000`]
- `LOG_LEVEL`: Logging level [default: `INFO`]

### Downloading MITIE Models

#### Option 1: Automated Download (Recommended)

Use the provided script to automatically download and extract MITIE models:

```bash
# Download Spanish MITIE models (~451MB)
./download_mitie_models.sh
```

The script will:
- Download the Spanish model ZIP file from GitHub releases
- Extract to the correct directory structure (`MITIE-models/spanish/`)
- Verify the download integrity
- Provide usage instructions

#### Option 2: Manual Download

If you prefer to download MITIE models manually:

```bash
# Download manually
curl -L -o MITIE-models-Spanish.zip \
  https://github.com/mit-nlp/MITIE/releases/download/v0.4/MITIE-models-v0.2-Spanish.zip

# Extract to correct location
mkdir -p temp_extract
unzip MITIE-models-Spanish.zip -d temp_extract
mv temp_extract/MITIE-models ./MITIE-models
rm -rf temp_extract MITIE-models-Spanish.zip
```

#### Docker Usage with Local Models

```bash
# After downloading models locally, mount in Docker
docker run -p 8000:8000 -v ./MITIE-models:/app/MITIE-models:ro spanish-ner:latest
```

## Performance Comparison

### MITIE Backend (Default)
- **Speed**: Moderate processing speed
- **Memory**: Higher usage (~451MB model)
- **Accuracy**: State-of-the-art precision with SVM and real confidence scores
- **Startup**: Slower model loading (~5-10 seconds)
- **Score Filtering**: Only high-confidence entities (>= 0.5) returned
- **Best for**: Applications requiring maximum accuracy and reliable confidence scores

### spaCy Backend
- **Speed**: Very fast processing
- **Memory**: Low usage (~93MB model)
- **Accuracy**: 89.01% F-score for Spanish NER
- **Startup**: Quick model loading (~1-2 seconds)
- **Score**: Fixed confidence score of 0.95 for all entities
- **Best for**: High-throughput applications, resource-constrained environments

### Common Features
- **Unique entities**: Automatic deduplication ensures no duplicate entities
- **Same API**: Identical interface regardless of backend
- **Entity types**: Both support PERSON, LOCATION, ORGANIZATION, MISC, PLACE

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Issues

Please report bugs and feature requests at: https://github.com/drzippie/ner-service/issues

## Acknowledgments

- **spaCy** for the excellent NLP library and Spanish models
- **Explosion AI** for maintaining high-quality language models
- **MIT NLP** for the MITIE information extraction library
- **FastAPI** for the web framework
- **Click** for the CLI framework