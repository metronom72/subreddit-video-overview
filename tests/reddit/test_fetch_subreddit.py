import os
from collections import UserList
from unittest.mock import Mock, patch
import praw
from praw.models import Comment

from src.reddit.fetch_subreddit import get_top_comments_from_post, reddit, extract_comment_data, fetch_subreddit
import unittest
import sys

sys.path.insert(0, '/path_to_directory/src/reddit')


class CommentMock:
    def __init__(self, author, score, body, replies=None):
        self.author = author
        self.score = score
        self.body = body
        self.replies = Mock()
        self.replies.list = Mock(return_value=replies if replies else [])


class TestReddit(unittest.TestCase):
    def setUp(self):
        # Initializing mocks for comments
        self.comment1 = CommentMock('user1', 100, 'test comment 1')
        self.comment2 = CommentMock('user2', 32, 'test comment 2', [self.comment1])
        self.comment3 = CommentMock('user3', 29, 'test comment 3', [self.comment1])

    @patch('os.getenv')
    @patch('praw.Reddit')
    def test_reddit(self, mock_praw, mock_getenv):
        # Arrange
        mock_getenv.side_effect = lambda key: {
            'CLIENT_ID': 'client_id',
            'CLIENT_SECRET': 'client_secret',
            'USER_AGENT': 'user_agent'
        }.get(key)

        # Act
        reddit_object = reddit()

        # Assert
        mock_praw.assert_called_once_with(client_id='client_id',
                                          client_secret='client_secret',
                                          user_agent='user_agent')

    @patch('src.reddit.fetch_subreddit.reddit')
    def test_get_top_comments_from_post(self, mock_reddit_func):
        mock_comment_1 = Mock()
        mock_comment_1.score = 20

        mock_comment_2 = Mock()
        mock_comment_2.score = 10

        mock_comment_3 = Mock()
        mock_comment_3.score = 15

        mock_comments = [mock_comment_1, mock_comment_2, mock_comment_3]

        mock_submission = Mock()
        mock_submission.comments.list.return_value = mock_comments

        mock_reddit_instance = Mock()
        mock_reddit_instance.submission.return_value = mock_submission

        mock_reddit_func.return_value = mock_reddit_instance

        # Testing with default limit
        url = 'http://test.com'
        result = get_top_comments_from_post(url)
        expected = [mock_comment_1, mock_comment_3, mock_comment_2]

        self.assertEqual(result, expected[:30])

        # Testing with specified limit
        limit = 2
        result = get_top_comments_from_post(url, limit)
        expected = [mock_comment_1, mock_comment_3]

        self.assertEqual(result, expected)

    def test_extract_single_comment(self):
        comment_data = extract_comment_data(self.comment1)
        self.assertEqual(len(comment_data), 1)
        self.assertEqual(comment_data[0]['author'], 'user1')
        self.assertEqual(comment_data[0]['votes'], 100)
        self.assertEqual(comment_data[0]['comment'], 'test comment 1')
        self.assertEqual(comment_data[0]['indent'], 0)

    def test_extract_comment_with_replies(self):
        comment_data = extract_comment_data(self.comment2)
        self.assertEqual(len(comment_data), 2)
        self.assertEqual(comment_data[0]['author'], 'user2')
        self.assertEqual(comment_data[0]['votes'], 32)
        self.assertEqual(comment_data[0]['comment'], 'test comment 2')
        self.assertEqual(comment_data[0]['indent'], 0)
        self.assertEqual(comment_data[1]['author'], 'user1')
        self.assertEqual(comment_data[1]['votes'], 100)
        self.assertEqual(comment_data[1]['comment'], 'test comment 1')
        self.assertEqual(comment_data[1]['indent'], 1)

    def test_extract_comment_with_low_score_replies(self):
        comment_data = extract_comment_data(self.comment3)
        self.assertEqual(len(comment_data), 2)
        self.assertEqual(comment_data[0]['author'], 'user3')
        self.assertEqual(comment_data[0]['votes'], 29)
        self.assertEqual(comment_data[0]['comment'], 'test comment 3')
        self.assertEqual(comment_data[0]['indent'], 0)
        self.assertEqual(comment_data[1]['author'], 'user1')
        self.assertEqual(comment_data[1]['votes'], 100)
        self.assertEqual(comment_data[1]['comment'], 'test comment 1')
        self.assertEqual(comment_data[1]['indent'], 1)

    @patch('src.reddit.fetch_subreddit.reddit')
    @patch('builtins.input', return_value='output.csv')
    def test_fetch_subreddit_default(self, mock_input, mock_reddit_func):
        mock_comment_1 = CommentMock('user1', 20, 'Comment 1')
        mock_comment_2 = CommentMock('user2', 10, 'Comment 2')
        mock_comment_3 = CommentMock('user3', 15, 'Comment 3')

        mock_comments = [mock_comment_1, mock_comment_2, mock_comment_3]

        mock_submission = Mock()
        mock_submission.comments.list.return_value = mock_comments

        mock_reddit_instance = Mock()
        mock_reddit_instance.submission.return_value = mock_submission

        mock_reddit_func.return_value = mock_reddit_instance

        fetch_subreddit('https://www.reddit.com/r/Python/comments/test_post', 10)

        mock_reddit_instance.submission.assert_called_once_with(url='https://www.reddit.com/r/Python/comments/test_post')
        mock_submission.comments.list.assert_called_once()


if __name__ == '__main__':
    unittest.main()
