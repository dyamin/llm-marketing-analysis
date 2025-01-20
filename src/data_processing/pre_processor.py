import json
import time

from src.common.constants import RAW_MSP_DATA_PATH, PROCESSED_MSP_DATA_PATH
from src.common.logger import get_logger
from src.data_processing.providers.gemini import process_content_with_genai

logger = get_logger(__name__)


def main():
    with open(RAW_MSP_DATA_PATH, "r", encoding="utf-8") as f:
        all_posts = json.load(f)

    logger.info(f"Loaded {len(all_posts)} posts from {RAW_MSP_DATA_PATH}")

    processed_posts = []
    for idx, post in enumerate(all_posts, start=1):
        logger.info(f"Processing post {idx}/{len(all_posts)} - ID: {post['id']}")

        # Build the text for the top-level post
        post_text = f"{post['title']}\n\n{post['selftext']}"
        post_result = process_content_with_genai(post_text)

        logger.info(f"Post summary: {post_result.get('summary', '')}")

        # Process comments
        processed_comments = []
        comments_list = post.get("comments", [])
        for c_idx, comment in enumerate(comments_list, start=1):
            logger.info(f"  Processing comment {c_idx}/{len(comments_list)} - ID: {comment['comment_id']}")
            comment_text = f"[By {comment['author']}]\n{comment['body']}"
            comment_result = process_content_with_genai(comment_text)

            logger.info(f"  Comment summary: {comment_result.get('summary', '')}")

            processed_comments.append({
                "comment_id": comment["comment_id"],
                "author": comment["author"],
                "body": comment["body"],
                "summary": comment_result.get("summary", ""),
                "sentiment_s1": comment_result.get("sentiment_s1", "unknown").lower(),
                "benefits_mentioned": comment_result.get("benefits_mentioned", []),
                "complaints_mentioned": comment_result.get("complaints_mentioned", []),
                "competitors_mentioned": comment_result.get("competitors_mentioned", []),
                "overall_tone": comment_result.get("overall_tone", "unknown"),
                "action_needed": comment_result.get("action_needed", "no_action"),
                "action_reason": comment_result.get("action_reason", ""),
                "suggested_response": comment_result.get("suggested_response", ""),
            })

            # Rate-limiting to stay under free-tier usage
            time.sleep(3)

        # Combine post result + comments
        processed_post = {
            "post_id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "created_utc": post["created_utc"],
            "query_matched": post["query_matched"],
            "llm_summary": post_result.get("summary", ""),
            "sentiment_s1": post_result.get("sentiment_s1", "unknown"),
            "benefits_mentioned": post_result.get("benefits_mentioned", []),
            "complaints_mentioned": post_result.get("complaints_mentioned", []),
            "competitors_mentioned": post_result.get("competitors_mentioned", []),
            "overall_tone": post_result.get("overall_tone", "unknown"),
            "action_needed": post_result.get("action_needed", "no_action"),
            "action_reason": post_result.get("action_reason", ""),
            "suggested_response": post_result.get("suggested_response", ""),
            "comments": processed_comments
        }

        # Append to our list
        processed_posts.append(processed_post)

        # Write partial progress to disk (in case script is interrupted)
        _save_partial_results(processed_posts)

        # Additional time.sleep if you want to ensure ~15 requests/min
        time.sleep(3)

    logger.info(f"Processing completed. {len(processed_posts)} posts processed.")


def _save_partial_results(processed_posts):
    """
    Helper to write the current list of processed posts to disk.
    """
    try:
        with open(PROCESSED_MSP_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(processed_posts, f, ensure_ascii=False, indent=2)
        logger.info(f"Wrote partial results: {len(processed_posts)} posts => {PROCESSED_MSP_DATA_PATH}")
    except Exception as e:
        logger.error(f"Error writing partial results: {e}")


if __name__ == "__main__":
    main()
