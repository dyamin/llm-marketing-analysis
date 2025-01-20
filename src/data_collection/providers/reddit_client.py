from typing import Optional

import praw

from src.common.constants import MAX_POSTS
from src.common.logger import get_logger

logger = get_logger(__name__)


class RedditClient:
    """
    A wrapper around the PRAW Reddit client that simplifies common tasks.
    """

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            user_agent: str,
            username: Optional[str],
            password: Optional[str]
    ):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

    def fetch_submissions(
            self,
            subreddit_name: str,
            query: str,
            limit: int = MAX_POSTS,
            sort: str = "new"
    ):
        """
        Fetch submissions from a given subreddit matching a query.
        """
        try:
            logger.info(f"Searching for '{query}' in r/{subreddit_name} (limit={limit}, sort={sort}).")
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = subreddit.search(
                query=query,
                sort=sort,
                limit=limit
            )
            return submissions
        except Exception as e:
            logger.error(f"Error fetching submissions: {e}")
            raise

    def fetch_comments_for_submission(self, submission_id: str, limit: Optional[int]):
        """
        Fetch comments from a single submission by ID.
        """
        try:
            submission = self.reddit.submission(id=submission_id)
            submission.comment_limit = limit or 100
            submission.comment_sort = "top"
            submission.comments.replace_more(0)
            return submission.comments.list()
        except Exception as e:
            logger.error(f"Error fetching comments for submission {submission_id}: {e}")
            raise
