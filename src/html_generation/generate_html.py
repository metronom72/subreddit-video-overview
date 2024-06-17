import os

from jinja2 import Template


def generate_html(row, output_file, version='v1'):
    """
    :param row: Dictionary containing the data for generating the HTML.
    :param output_file: Path to the output file where the generated HTML will be saved.
    :param version: (optional) Version of the template to use. Default is 'v1'.
    :return: None

    This method generates an HTML file based on the provided data and saves it to the specified output file.

    The method reads the template HTML file located in 'src/html_generation/templates/{version}/template.html' and uses it as a base for the generated HTML. It also optionally reads a CSS file located in 'src/html_generation/templates/{version}/style.css' and includes its content in the generated HTML.

    The 'row' parameter should be a dictionary containing the necessary data for generating the HTML. It should have the following keys and corresponding values:
        - 'author': The author of the content.
        - 'votes': The number of votes received.
        - 'comment': The comment associated with the content.

    The 'output_file' parameter should be a string representing the path to the output file where the generated HTML will be saved.

    The 'version' parameter is optional and defaults to 'v1'. It specifies the version of the template to use. The template should be located in the corresponding folder under 'src/html_generation/templates'.

    Example usage:
        generate_html(row={'author': 'John Doe', 'votes': 10, 'comment': 'Great post'},
                      output_file='output.html',
                      version='v2')
    """
    with open(f'src/html_generation/templates/{version}/template.html', 'r') as file:
        template = Template(file.read())

    css_file = f'src/html_generation/templates/{version}/style.css'
    css_content = ""
    if os.path.exists(css_file):
        with open(css_file, 'r') as file:
            css_content = file.read()

    html_content = template.render(author=row['author'], votes=row['votes'], comment=row['comment'], css_content=css_content)

    with open(output_file, 'w') as file:
        file.write(html_content)