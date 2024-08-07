import csv
import os
from urllib.parse import urlparse

import praw
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def reddit():
    # Get variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    user_agent = os.getenv('USER_AGENT')

    return praw.Reddit(client_id=client_id,
                       client_secret=client_secret,
                       user_agent=user_agent)


def get_top_comments_from_post(url, limit=30):
    """
    Get the top comments from a post.

    :param url: The URL of the post.
    :param limit: The maximum number of comments to retrieve (default: 30).

    :return A list of top comments, sorted by score (number of votes).
    """
    submission = reddit().submission(url=url)
    submission.comments.replace_more(limit=0)  # Remove "load more comments" instances
    comments = submission.comments.list()

    # Sort comments by score (number of votes)
    top_comments = sorted(comments, key=lambda comment: comment.score, reverse=True)

    print(f"top_comments[:limit]: {top_comments[:limit]}")

    # Get top N comments
    return top_comments[:limit]


def extract_comment_data(comment, indent=0):
    """
    Extracts data from a comment and its subcomments recursively.

    :param comment: The comment to extract data from.
    :type comment: praw.models.Comment
    :param indent: The indentation level of the comment.
    :type indent: int
    :return A list of dictionaries with the extracted comment data.
    :rtype list[dict]
    """
    comments_data = [{
        'author': str(comment.author),
        'votes': comment.score,
        'comment': comment.body,
        'indent': indent
    }]
    subcomments = comment.replies.list()
    for subcomment in subcomments:
        if subcomment.score > 30:
            comments_data.extend(extract_comment_data(subcomment, indent + 1))
    return comments_data


def fetch_subreddit(post_url, limit, default_name=False):
    """
    Fetches the top comments from a given post URL and writes them to a user-specified CSV file.
    The default output file name is based on the last path segment of the post URL.

    :param default_name:
    :param post_url: The URL of the post to fetch comments from.
    :param limit: The number of top comments to fetch.
    :return None
    """
    comments = get_top_comments_from_post(post_url, limit)

    comments_data = []
    for comment in comments:
        comments_data.extend(extract_comment_data(comment))

    # Extract the last path segment from the URL and use it as the default file name
    parsed_url = urlparse(post_url)
    path_segments = parsed_url.path.split('/')
    default_file_name = path_segments[-2] + '.csv' if path_segments[-1] == '' else path_segments[-1] + '.csv'

    # Prompt user for the output file name with a default value
    if default_name:
        output_file = default_file_name
    else:
        output_file = input(f"Enter the name for the output CSV file (default: {default_file_name}): ")

    if not output_file:
        output_file = f'samples/{default_file_name}'

    # Write data to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['author', 'votes', 'comment', 'indent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in comments_data:
            writer.writerow(data)

    print(f"Top {limit} comments from the post have been written to {output_file}.")
