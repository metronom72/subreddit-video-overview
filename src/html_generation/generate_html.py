import os
import time
import json
from jinja2 import Template
import pandas as pd


def read_file(file_path):
    """Read the content of a file and return its content and size."""
    start_time = time.time()
    with open(file_path, 'r') as file:
        content = file.read()
    size = os.path.getsize(file_path)
    read_time = time.time() - start_time
    return content, size, read_time


def get_metadata(file_path):
    """Return metadata for the file if it exists, otherwise return error metadata."""
    if os.path.exists(file_path):
        content, size, read_time = read_file(file_path)
        return content, {
            'file': file_path,
            'size': size,
            'read_time': read_time
        }
    else:
        return "", {
            'file': file_path,
            'size': 0,
            'read_time': 0,
            'error': 'File not found'
        }


def render_html(row, template_content, css_content, js_content):
    """Render the HTML content using the provided template and additional content."""
    start_time = time.time()
    template = Template(template_content)
    html_content = template.render(
        author=row['author'],
        votes=row['votes'],
        comment=row['comment'],
        css_content=css_content,
        js_content=js_content
    )
    generation_time = time.time() - start_time
    return html_content, generation_time


def write_output_file(output_file, content):
    """Write the content to the output file and return the size and write time."""
    start_time = time.time()
    with open(output_file, 'w') as file:
        file.write(content)
    size = os.path.getsize(output_file)
    write_time = time.time() - start_time
    return size, write_time


def generate_html(row, output_file, version='v1'):
    template_file = f'src/html_generation/templates/{version}/template.html'
    css_file = f'src/html_generation/templates/{version}/style.css'
    js_file = f'src/html_generation/templates/{version}/script.js'

    # Ensure row is a dictionary and JSON serializable
    if isinstance(row, pd.Series):
        row = row.to_dict()
    elif not isinstance(row, dict):
        raise TypeError("Row must be a dictionary or a Pandas Series convertible to a dictionary")

    # Initialize metadata for this HTML generation
    metadata = {
        'version': version,
        'row': row  # Add the row data to the metadata
    }

    # Get template metadata
    template_content, template_metadata = get_metadata(template_file)
    metadata['template'] = template_metadata

    # Get CSS metadata
    css_content, css_metadata = get_metadata(css_file)
    metadata['css'] = css_metadata

    # Get JavaScript metadata
    js_content, js_metadata = get_metadata(js_file)
    metadata['js'] = js_metadata

    # Render HTML content
    html_content, generation_time = render_html(row, template_content, css_content, js_content)
    metadata['html_generation'] = {
        'generation_time': generation_time
    }

    # Write HTML content to output file
    output_size, write_time = write_output_file(output_file, html_content)
    metadata['output'] = {
        'file': output_file,
        'size': output_size,
        'write_time': write_time
    }

    # Define the path for the metadata file
    metadata_file = os.path.join(os.path.dirname(output_file), 'html_metadata.json')

    # Read existing metadata if the file exists
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            existing_metadata = json.load(file)
    else:
        existing_metadata = []

    # Append the new metadata to the existing metadata
    existing_metadata.append(metadata)

    # Write the updated metadata back to the JSON file
    with open(metadata_file, 'w') as file:
        json.dump(existing_metadata, file, indent=4)

    print(f"Metadata written to '{metadata_file}'")