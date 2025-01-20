import json
from collections import defaultdict

from src.common.constants import PROCESSED_MSP_DATA_PATH, ANALYSIS_RESULTS_PATH
from src.common.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Reads the processed JSON from the LLM pipeline, then:
      - Aggregates top-level sentiment & competitor mentions
      - Finds actionable items and organizes them
      - Produces a final analysis & suggestions
    """
    with open(PROCESSED_MSP_DATA_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)

    logger.info(f"Loaded {len(posts)} posts from {PROCESSED_MSP_DATA_PATH}")

    # Aggregate general info
    competitor_counts = defaultdict(int)  # how often each competitor is mentioned
    s1_sentiment_counts = defaultdict(int)  # distribution of sentiment_s1 across all posts/comments
    actionable_items = []  # list of (post/comment) needing action

    # For final “top-level summary”
    total_posts = len(posts)
    total_comments = 0
    mention_sentinelone = 0  # how many posts mention or discuss SentinelOne in some capacity

    for post in posts:
        # check if this post text references S1 (the logic is up to you; we can check 'sentiment_s1' != 'not mentioned')
        if post["sentiment_s1"] != "not mentioned":
            mention_sentinelone += 1

        # Tally sentiment
        s1_sentiment_counts[post["sentiment_s1"]] += 1

        # Tally competitor mentions for the post
        for comp in post["competitors_mentioned"]:
            competitor_counts[comp] += 1

        # Check if post is actionable
        if post["action_needed"] == "yes":
            actionable_items.append({
                "type": "post",
                "post_id": post["post_id"],
                "title": post["title"],
                "action_reason": post["action_reason"],
                "suggested_response": post["suggested_response"],
            })

        # Now handle comments
        for comment in post["comments"]:
            total_comments += 1

            # Tally sentiment
            s1_sentiment_counts[comment["sentiment_s1"]] += 1

            # Tally competitor mentions
            for comp in comment["competitors_mentioned"]:
                competitor_counts[comp] += 1

            # Check if comment is actionable
            if comment["action_needed"] == "yes":
                actionable_items.append({
                    "type": "comment",
                    "post_id": post["post_id"],
                    "comment_id": comment["comment_id"],
                    "author": comment["author"],
                    "action_reason": comment["action_reason"],
                    "suggested_response": comment["suggested_response"]
                })

    # Build final aggregated insights
    # S1 Sentiment distribution
    # E.g., how many times we saw "positive", "negative", "neutral", "not mentioned", etc.
    s1_sentiment_distribution = dict(s1_sentiment_counts)

    # Sort competitor counts descending
    sorted_competitors = sorted(competitor_counts.items(), key=lambda x: x[1], reverse=True)
    competitor_summary = [{"competitor": c, "mentions": count} for c, count in sorted_competitors if c]

    # Summaries and suggestions
    main_findings = {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "posts_with_s1_mentioned": mention_sentinelone,
        "s1_sentiment_distribution": s1_sentiment_distribution,
        "competitors_mentioned_summary": competitor_summary
    }

    # Construct final output
    analysis_output = {
        "main_findings": main_findings,
        "actionable_items": actionable_items
    }

    with open(ANALYSIS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis_output, f, ensure_ascii=False, indent=2)

    logger.info(f"Analysis complete. Wrote {len(actionable_items)} actionable items to {ANALYSIS_RESULTS_PATH}.")


if __name__ == "__main__":
    main()
