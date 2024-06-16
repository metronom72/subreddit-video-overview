def generate_html(row, template, output_file):
    html_content = template.render(author=row['author'], votes=row['votes'], comment=row['comment'])

    with open(output_file, 'w') as file:
        file.write(html_content)