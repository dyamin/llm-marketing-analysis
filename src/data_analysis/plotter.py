import json
import os
from textwrap import wrap

import matplotlib.pyplot as plt

from src.common.constants import ANALYSIS_RESULTS_PATH, REPORTS_DIR


def main():
    if not os.path.exists(ANALYSIS_RESULTS_PATH):
        print(f"Error: {ANALYSIS_RESULTS_PATH} not found.")
        return

    with open(ANALYSIS_RESULTS_PATH, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    main_findings = analysis["main_findings"]
    actionable_items = analysis["actionable_items"]

    # Visualize S1 Sentiment Distribution
    sentiment_dist = main_findings["s1_sentiment_distribution"]

    # Prepare data for plotting
    sentiments = list(sentiment_dist.keys())
    counts = list(sentiment_dist.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(sentiments, counts, color="teal")
    plt.title("SentinelOne Sentiment Distribution", fontsize=16)
    plt.xlabel("Sentiment Category")
    plt.ylabel("Count")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.5,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "sentiment_distribution.png"))  # Save the figure
    plt.show()

    # Visualize Competitor Mentions
    competitors = main_findings[
        "competitors_mentioned_summary"]

    # Sort or filter out extremely low mentions if it’s too large
    top_competitors = competitors[:10]

    competitor_names = [item["competitor"] for item in top_competitors]
    competitor_counts = [item["mentions"] for item in top_competitors]

    plt.figure(figsize=(10, 6))
    bars_comp = plt.bar(competitor_names, competitor_counts, color="cornflowerblue")
    plt.title("Top 10 Competitor Mentions", fontsize=16)
    plt.xlabel("Competitor")
    plt.ylabel("Number of Mentions")
    plt.xticks(rotation=45, ha="right")

    # Add data labels
    for bar in bars_comp:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.3,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "competitor_mentions.png"))
    plt.show()

    # Display a small "table" of actionable items
    # We can show in console or do a textual summary
    print("\n=== ACTIONABLE ITEMS ===")
    for i, item in enumerate(actionable_items, start=1):
        # Wrap the text so it doesn't run off the screen
        reason_wrapped = "\n".join(wrap(item["action_reason"], width=60))
        response_wrapped = "\n".join(wrap(item["suggested_response"], width=60))

        # type could be "post" or "comment"
        item_type = item.get("type", "comment")
        if item_type == "post":
            print(f"\n{i}. POST {item['post_id']} - {item.get('title', '')}")
        else:
            print(f"\n{i}. COMMENT {item['comment_id']} on Post {item['post_id']} by {item.get('author', '')}")

        print(f"   Reason: {reason_wrapped}")
        print(f"   Suggested Response:\n   {response_wrapped}")

    print("\nDone visualizing!")


if __name__ == "__main__":
    main()
