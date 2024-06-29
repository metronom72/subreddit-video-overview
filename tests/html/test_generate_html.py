import json
import os
import time
import unittest
from unittest.mock import mock_open, patch

import pandas as pd

from src.html import generate_html
from src.html.generate_html import render_html, generate_html as generate_html_function


class TestGenerateHtml(unittest.TestCase):

    def setUp(self):
        self.mock_file_content = "Mock file content."
        self.existing_file = "./some_existing_file"
        self.non_existing_file = "./some_bogus_file"
        self.metadata_keys = ['file', 'size', 'read_time']

        with open(self.existing_file, "w") as f:
            f.write("Hello, World!")

        self.row = {
            'author': 'John Doe',
            'votes': 55,
            'comment': 'Hello, world!'
        }
        self.template_content = """
        <div>
            <h1>{{ author }}</h1>
            <p>{{ comment }}<p>
            <p>Votes: {{ votes }}</p>
            <style>{{ css_content }}</style>
            <script>{{ js_content }}</script>
        </div>
        """
        self.css_content = 'body {background-color: powderblue;}'
        self.js_content = 'console.log("Page loaded");'

        self.test_dict_row = {'data': 'test'}
        self.test_series_row = pd.Series(self.test_dict_row)
        self.test_output_file = 'test.html'
        self.test_metadata_file = 'html_metadata.json'

    def tearDown(self):
        # Remove the file after all tests are done
        if os.path.exists(self.existing_file):
            os.remove(self.existing_file)

        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)
        if os.path.exists('html_metadata.json'):
            os.remove('html_metadata.json')

    def test_render_html(self):
        html, gen_time = render_html(self.row, self.template_content, self.css_content, self.js_content)
        self.assertIn(self.row['author'], html)
        self.assertIn(self.row['comment'], html)
        self.assertIn(str(self.row['votes']), html)
        self.assertIn(self.css_content, html)
        self.assertIn(self.js_content, html)
        self.assertTrue(gen_time >= 0)

    def test_split_by_newlines_empty(self):
        result = generate_html.split_by_newlines('')
        self.assertEqual(result, [''],
                         "Expected [''] for empty input but got {0}".format(result))

    def test_split_by_newlines_single_newline(self):
        result = generate_html.split_by_newlines('hello\nworld')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    def test_split_by_newlines_multiple_newlines(self):
        result = generate_html.split_by_newlines('hello\n\nworld')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    def test_split_by_newlines_leading_trailing_spaces(self):
        result = generate_html.split_by_newlines('  hello\nworld  ')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    def test_split_by_newlines_multiple_space_newlines(self):
        result = generate_html.split_by_newlines('  hello\n\n   world  ')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    def test_split_by_newlines_crlf(self):
        result = generate_html.split_by_newlines('hello\r\nworld')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    def test_split_by_newlines_crlf_with_spaces(self):
        result = generate_html.split_by_newlines('  hello\r\n   world  ')
        self.assertEqual(result, ['hello', 'world'],
                         "Expected ['hello', 'world'] but got {0}".format(result))

    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open)
    def test_read_file(self, mock_open_file, mock_getsize):
        """Test the read_file method."""
        mock_open_file.return_value.read.return_value = self.mock_file_content
        mock_getsize.return_value = len(self.mock_file_content)

        start_time = time.time()
        file_path = '/path/to/mock/file'
        result = generate_html.read_file(file_path)

        # Assert the file was opened.
        mock_open_file.assert_called_once_with(file_path, 'r')

        # Assert file size getter was called.
        mock_getsize.assert_called_once_with(file_path)

        self.assertEqual(result[0], self.mock_file_content, "File content mismatch.")
        self.assertEqual(result[1], len(self.mock_file_content), "File size mismatch.")

        # Check that reading operation didn't take more than 5 seconds.
        end_time = time.time()
        self.assertLess(end_time - start_time, 5)

    def test_get_metadata_existing_file(self):
        content, metadata = generate_html.get_metadata(self.existing_file)

        self.assertEqual(content, "Hello, World!")
        self.assertIn('file', metadata)
        self.assertIn('size', metadata)
        self.assertIn('read_time', metadata)
        self.assertNotIn('error', metadata)

    def test_get_metadata_non_existing_file(self):
        content, metadata = generate_html.get_metadata(self.non_existing_file)

        self.assertEqual(content, "")
        self.assertIn('file', metadata)
        self.assertIn('size', metadata)
        self.assertIn('read_time', metadata)
        self.assertIn('error', metadata)
        self.assertEqual(metadata['error'], 'File not found')

    @patch('os.path.getsize', return_value=10)
    @patch('time.time', side_effect=[1000, 2000])
    @patch('builtins.open', new_callable=mock_open)
    def test_write_output_file(self, mock_file, mock_time, mock_getsize):
        size, time_taken = generate_html.write_output_file("output.html", "Hello, World!")

        mock_file.assert_called_once_with("output.html", 'w')
        mock_file().write.assert_called_once_with("Hello, World!")

        self.assertEqual(size, 10)
        self.assertEqual(time_taken, 1000)

    @patch("src.html.generate_html.get_metadata")
    @patch("src.html.generate_html.render_html")
    @patch("src.html.generate_html.write_output_file")
    def test_generate_html_with_dict_and_valid_version(self, mock_write_output_file, mock_render_html, mock_get_metadata):
        mock_write_output_file.return_value = 1000, 1  # returns output_size, write_time
        mock_render_html.return_value = "html_content", 0.1  # returns html_content, generation_time
        mock_get_metadata.return_value = "", {}  # returns content, metadata
        generate_html_function(self.test_dict_row, self.test_output_file, 'v1')
        with open(self.test_metadata_file, 'r') as f:
            metadata = json.load(f)
        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0]["version"], 'v1')

    @patch("src.html.generate_html.get_metadata")
    @patch("src.html.generate_html.render_html")
    @patch("src.html.generate_html.write_output_file")
    def test_generate_html_with_series_and_valid_version(self, mock_write_output_file, mock_render_html, mock_get_metadata):
        mock_write_output_file.return_value = 1000, 1  # returns output_size, write_time
        mock_render_html.return_value = "html_content", 0.1  # returns html_content, generation_time
        mock_get_metadata.return_value = "", {}  # returns content, metadata
        generate_html_function(self.test_series_row, self.test_output_file, 'v1')
        with open(self.test_metadata_file, 'r') as f:
            metadata = json.load(f)
        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0]["version"], 'v1')

    def test_generate_html_with_invalid_data_type_for_row(self):
        with self.assertRaises(TypeError):
            generate_html_function("invalid_data_type_for_row", self.test_output_file, 'v1')



if __name__ == '__main__':
    unittest.main()
