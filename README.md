# Spanish NER Service

A Python application for Named Entity Recognition (NER) in Spanish using state-of-the-art transformer models. Provides both a command-line interface and a REST API for extracting named entities from Spanish text.

## Features

- **State-of-the-art Models**: Uses PlanTL-GOB-ES RoBERTa model with BETO fallback
- **Multiple Interfaces**: Command-line tool and REST API
- **Entity Types**: PERSON, LOCATION, ORGANIZATION, MISC, PLACE
- **Flexible Output**: JSON, table, and simple text formats
- **Fast API**: Built with FastAPI for high performance
- **Interactive Documentation**: Automatic API documentation with Swagger UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/drzippie/ner-service.git
cd ner-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Analyze text directly:
```bash
python -m src.cli "Juan lives in Madrid and works at Google Spain."
```

Analyze text from file:
```bash
python -m src.cli --file input.txt --format table
```

Save results to file:
```bash
python -m src.cli "María studied in Barcelona" --output results.json
```

#### CLI Options

- `--file, -f`: Input text file to analyze
- `--output, -o`: Output file for results
- `--format`: Output format (`json`, `table`, `simple`)
- `--quiet, -q`: Suppress informational messages
- `--help`: Show help message

### Web API

Start the server:
```bash
python -m src.web_server
```

The API will be available at `http://localhost:8000`

#### API Endpoints

- **POST /ner**: Analyze text for named entities
- **GET /health**: Check API status
- **GET /docs**: Interactive API documentation
- **GET /**: API information

#### Example API Usage

```bash
curl -X POST "http://localhost:8000/ner" \
     -H "Content-Type: application/json" \
     -d '{"text": "Juan lives in Madrid and works at Google Spain."}'
```

Response:
```json
{
  "entities": [
    {
      "tag": "PERSON",
      "score": "0.9998",
      "label": "Juan"
    },
    {
      "tag": "LOCATION",
      "score": "0.9995",
      "label": "Madrid"
    },
    {
      "tag": "ORGANIZATION",
      "score": "0.9987",
      "label": "Google Spain"
    }
  ]
}
```

## Models

The service uses the following transformer models:

1. **Primary**: `PlanTL-GOB-ES/roberta-base-bne-capitel-ner` - Spanish RoBERTa model trained on the National Library of Spain corpus
2. **Fallback**: `mrm8488/bert-spanish-cased-finetuned-ner` - BETO (Spanish BERT) fine-tuned for NER

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
  "score": "0.9999",
  "label": "Entity Name"
}
```

- `tag`: The entity type (PERSON, LOCATION, etc.)
- `score`: Confidence score from the model (0.0 to 1.0)
- `label`: The actual text of the identified entity

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

- Python 3.8+
- PyTorch
- Transformers (HuggingFace)
- FastAPI
- Click
- Uvicorn

See `requirements.txt` for specific versions.

## Performance

The service automatically handles model loading and caching for optimal performance. First-time model download may take a few minutes, but subsequent runs will be much faster.

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

- **PlanTL-GOB-ES** for the Spanish RoBERTa models
- **HuggingFace** for the Transformers library
- **FastAPI** for the web framework
- **Click** for the CLI framework