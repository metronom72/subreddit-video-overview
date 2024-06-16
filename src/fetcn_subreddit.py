import praw
import csv

# Reddit API credentials
client_id = 'w7BZhB-NLf8RXHiTLkpjdg'
client_secret = 'AjVlh97m-WDeEtwV1-Q8hX_V1S7znw'
user_agent = 'python:my_reddit_bot:v1.0 (by /u/LevelRelationship732)'

# Initialize PRAW with your credentials
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)


def get_top_comments_from_post(url, limit=30):
    """
    Retrieve the top comments from a post.

    :param url: The URL of the post.
    :param limit: The maximum number of comments to retrieve.
    :return: A list of Comment objects representing the top comments.
    """
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)  # Remove "load more comments" instances
    comments = submission.comments.list()

    # Sort comments by score (number of votes)
    top_comments = sorted(comments, key=lambda comment: comment.score, reverse=True)

    # Get top N comments
    return top_comments[:limit]


def extract_comment_data(comment, indent=0):
    """
    Extracts data from a Reddit comment and its subcomments.

    :param comment: The comment to extract data from.
    :param indent: The indentation level of the comment.
    :return: A list of dictionaries containing the extracted data.
    """
    comments_data = []
    comments_data.append({
        'author': str(comment.author),
        'votes': comment.score,
        'comment': comment.body,
        'indent': indent
    })
    subcomments = comment.replies.list()
    for subcomment in subcomments:
        if subcomment.score > 30:
            comments_data.extend(extract_comment_data(subcomment, indent + 1))
    return comments_data


def fetch_subreddit(post_url, limit):
    """
    Fetches the top comments from a given post URL and writes the data to a CSV file.

    :param post_url: The URL of the post.
    :param limit: The maximum number of comments to fetch.
    :return: None
    """
    comments = get_top_comments_from_post(post_url, limit)

    comments_data = []
    for comment in comments:
        comments_data.extend(extract_comment_data(comment))

    # Write data to CSV
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = ['author', 'votes', 'comment', 'indent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in comments_data:
            writer.writerow(data)

    print(f"Top {limit} comments from the post have been written to output.csv.")
