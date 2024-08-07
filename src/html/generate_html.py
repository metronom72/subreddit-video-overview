import json
import os
import re
import shutil
import time

import pandas as pd
from jinja2 import Template


def split_by_newlines(text):
    """Splits the input string by any amount of new lines."""
    return [line.strip() for line in re.split(r'\n+', text.replace('\r', '').strip())]


def copy_css_js_files(version, destination_dir):
    """
    Copy CSS and JS files from source directory to destination directory.

    :param version: The version of the files to copy.
    :param destination_dir: The directory where the files will be copied to.
    :return: None
    """
    # Define the source and destination directories
    source_dir = f'src/html/templates/{version}/'

    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # Iterate through files in the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Check if the file has a .css or .js extension
            if file.endswith(('.css', '.js')):
                # Construct full file paths
                source_file = os.path.join(root, file)
                # Ensure subdirectories in the destination path are created
                relative_path = os.path.relpath(root, source_dir)
                destination_subdir = os.path.join(destination_dir, relative_path)
                os.makedirs(destination_subdir, exist_ok=True)
                destination_file = os.path.join(destination_subdir, file)
                # Copy file from source to destination
                shutil.copy(source_file, destination_file)
                print(f"Copied: {source_file} to {destination_file}")


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

    # Safely retrieve 'comment' from row, providing a default value if it does not exist
    comment = row.get('comment', '')

    html_content = template.render(
        author=row.get('author', 'Unknown Author'),  # Handle missing 'author' key with default value
        votes=row.get('votes', 0),  # Handle missing 'votes' key with default value
        comment=json.dumps(comment),
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
    split_comments = version not in ['v1', 'v2']
    combine_assets = version not in ['v4']

    css_file = None
    css_content = None

    js_file = None
    js_content = None

    template_file = f'src/html/templates/{version}/template.html'
    if combine_assets:
        css_file = f'src/html/templates/{version}/style.css'
        js_file = f'src/html/templates/{version}/script.js'
    else:
        copy_css_js_files(version, os.path.dirname(output_file))

    # Ensure row is a dictionary and JSON serializable
    if isinstance(row, pd.Series):
        row = row.to_dict()
        if split_comments:
            row['comment'] = split_by_newlines(row['comment'])
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

    if combine_assets:
        if css_file:
            # Get CSS metadata
            css_content, css_metadata = get_metadata(css_file)
            metadata['css'] = css_metadata

        if js_file:
            # Get JavaScript metadata
            js_content, js_metadata = get_metadata(js_file)
            metadata['js'] = js_metadata

        # Render HTML content
        html_content, generation_time = render_html(row,
                                                    template_content,
                                                    css_content or '',
                                                    js_content or '')
    else:
        # Render HTML content
        html_content, generation_time = render_html(row,
                                                    template_content,
                                                    '',
                                                    '')
    metadata['html'] = {
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
