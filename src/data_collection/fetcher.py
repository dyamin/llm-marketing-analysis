import json
import os
import time

from dotenv import load_dotenv

from src.common.constants import RAW_MSP_DATA_PATH, QUERIES, SUBREDDIT_NAME, MAX_POSTS
from src.common.logger import get_logger
from src.data_collection.providers.reddit_client import RedditClient

load_dotenv()

logger = get_logger(__name__)


def main():
    reddit_client = RedditClient(
        os.getenv("REDDIT_CLIENT_ID"),
        os.getenv("REDDIT_CLIENT_SECRET"),
        os.getenv("REDDIT_USER_AGENT"),
        os.getenv("REDDIT_USERNAME"),
        os.getenv("REDDIT_PASSWORD")
    )

    all_posts = []

    for q in QUERIES:
        submissions = reddit_client.fetch_submissions(
            subreddit_name=SUBREDDIT_NAME,
            query=q,
            limit=MAX_POSTS,
            sort="new"
        )

        for submission in submissions:
            try:
                post_data = {
                    "id": submission.id,
                    "title": submission.title,
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "created_utc": submission.created_utc,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "url": submission.url,
                    "query_matched": q,
                    "selftext": submission.selftext,
                    "platform": "reddit"
                }

                # Fetch a limited number of comments
                comments = reddit_client.fetch_comments_for_submission(
                    submission_id=submission.id,
                    limit=10
                )

                post_data["comments"] = []
                for comment in comments:
                    if not comment.body:
                        continue
                    post_data["comments"].append({
                        "comment_id": comment.id,
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": comment.created_utc
                    })

                all_posts.append(post_data)
                time.sleep(1)  # Be nice to Reddit's API

            except Exception as e:
                logger.error(f"Error processing submission {submission.id}: {e}")

    # Dump collected data
    with open(RAW_MSP_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    logger.info(f"Data collection complete. {len(all_posts)} posts saved to msp_data.json")


if __name__ == "__main__":
    main()
