import click
import json
import sys
from typing import Optional
from .ner_core import extract_entities

@click.command()
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.File('r'), help='Text file to analyze')
@click.option('--output', '-o', type=click.File('w'), help='Output file for results')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'table', 'simple']), 
              default='json',
              help='Output format (json, table, simple)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress informational messages')
@click.version_option(version='1.0.0', prog_name='Spanish NER CLI')
def main(text: Optional[str], file, output, output_format: str, quiet: bool):
    """
    Spanish NER CLI - Named Entity Recognition for Spanish
    
    Analyzes text and extracts named entities (PERSON, LOCATION, ORGANIZATION, MISC, PLACE).
    
    Examples:
    
        ner-cli "Juan lives in Madrid and works at Google."
        
        ner-cli --file text.txt --format table
        
        ner-cli "Maria studied in Barcelona" --output results.json
    """
    
    # Validate input
    if not text and not file:
        if not quiet:
            click.echo("Error: Must provide text as argument or use --file", err=True)
        click.echo("Use 'ner-cli --help' to see available options.", err=True)
        sys.exit(1)
    
    # Get text to analyze
    if file:
        try:
            text = file.read()
        except Exception as e:
            if not quiet:
                click.echo(f"Error reading file: {e}", err=True)
            sys.exit(1)
    
    if not text or not text.strip():
        if not quiet:
            click.echo("Error: Text is empty", err=True)
        sys.exit(1)
    
    # Process text
    try:
        if not quiet:
            click.echo("Analyzing text...", err=True)
        
        entities = extract_entities(text.strip())
        
        if not quiet:
            click.echo(f"Found {len(entities)} entities", err=True)
        
        # Format output
        result = format_output(entities, output_format)
        
        # Write result
        if output:
            try:
                output.write(result)
                if not quiet:
                    click.echo(f"Results saved to {output.name}", err=True)
            except Exception as e:
                if not quiet:
                    click.echo(f"Error writing file: {e}", err=True)
                sys.exit(1)
        else:
            click.echo(result)
            
    except Exception as e:
        if not quiet:
            click.echo(f"Error processing text: {e}", err=True)
        sys.exit(1)

def format_output(entities, format_type: str) -> str:
    """
    Format output according to specified type
    
    Args:
        entities: List of found entities
        format_type: Format type (json, table, simple)
        
    Returns:
        Formatted string
    """
    if format_type == 'json':
        return json.dumps({"entities": entities}, indent=2, ensure_ascii=False)
    
    elif format_type == 'table':
        if not entities:
            return "No entities found."
        
        # Calculate column widths
        max_tag = max(len(entity['tag']) for entity in entities)
        max_label = max(len(entity['label']) for entity in entities)
        max_score = max(len(entity['score']) for entity in entities)
        
        # Ensure minimum width for headers
        max_tag = max(max_tag, len('TYPE'))
        max_label = max(max_label, len('ENTITY'))
        max_score = max(max_score, len('SCORE'))
        
        # Create table
        header = f"{'TYPE':<{max_tag}} | {'ENTITY':<{max_label}} | {'SCORE':<{max_score}}"
        separator = "-" * len(header)
        
        lines = [header, separator]
        
        for entity in entities:
            line = f"{entity['tag']:<{max_tag}} | {entity['label']:<{max_label}} | {entity['score']:<{max_score}}"
            lines.append(line)
        
        return "\n".join(lines)
    
    elif format_type == 'simple':
        if not entities:
            return "No entities found."
        
        lines = []
        for entity in entities:
            lines.append(f"{entity['label']} ({entity['tag']}) - {entity['score']}")
        
        return "\n".join(lines)
    
    else:
        raise ValueError(f"Unsupported format: {format_type}")

@click.command()
@click.option('--host', default='0.0.0.0', help='Server host')
@click.option('--port', default=8000, help='Server port')
@click.option('--reload', is_flag=True, help='Auto-reload in development')
def server(host: str, port: int, reload: bool):
    """
    Start the FastAPI web server
    """
    try:
        import uvicorn
        from .web_server import app
        
        click.echo(f"Starting server at http://{host}:{port}")
        click.echo("Documentation available at http://localhost:8000/docs")
        
        uvicorn.run(app, host=host, port=port, reload=reload)
        
    except ImportError:
        click.echo("Error: uvicorn is not installed. Install it with: pip install uvicorn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        sys.exit(1)

@click.group()
def cli():
    """Spanish NER - Named Entity Recognition for Spanish"""
    pass

cli.add_command(main, name='analyze')
cli.add_command(server, name='server')

if __name__ == '__main__':
    main()