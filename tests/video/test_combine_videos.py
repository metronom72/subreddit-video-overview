import unittest
import os
from src.video.combine_videos import create_file_list


class TestCreateFileList(unittest.TestCase):
    
    def setUp(self):
        self.directory = './test_directory'
        self.file_list_path = './test_file_list.txt'
        os.makedirs(self.directory, exist_ok=True)
        
    def tearDown(self):
        os.unlink(self.file_list_path)
        for file in os.listdir(self.directory):
            os.unlink(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_create_file_list(self):
        # Arrange 
        test_filenames = ['test1_with_audio.mp4', 'test2_with_audio.mp4', 'test3.txt']
        for filename in test_filenames:
            open(os.path.join(self.directory, filename), 'a').close()
        
        # Act
        create_file_list(self.directory, self.file_list_path)
        
        # Assert
        with open(self.file_list_path, 'r') as f:
            contents = f.read()
        for filename in [os.path.join(self.directory, 'test1_with_audio.mp4'), 
                         os.path.join(self.directory, 'test2_with_audio.mp4')]:
            self.assertIn(f"file '{filename}'", contents)

    def test_empty_directory(self):
        # Arrange 
        # The directory is created empty in setUp
        
        # Act
        create_file_list(self.directory, self.file_list_path)
        
        # Assert
        with open(self.file_list_path, 'r') as f:
            contents = f.read()
        self.assertEqual(contents, '')