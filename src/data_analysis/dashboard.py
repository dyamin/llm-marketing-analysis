import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ANALYSIS_RESULTS_PATH = Path(__file__).parent.parent.parent / "data/processed/analysis_results.json"


def load_analysis_data(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def main():
    st.title("SentinelOne Analysis Dashboard")

    # Load Data
    try:
        analysis = load_analysis_data(ANALYSIS_RESULTS_PATH)
    except FileNotFoundError:
        st.error(f"File {ANALYSIS_RESULTS_PATH} not found. Please place your analysis JSON in this file path.")
        return

    main_findings = analysis["main_findings"]
    actionable_items = analysis["actionable_items"]

    # Display Main Findings as KPIs
    st.header("Main Findings")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", main_findings.get("total_posts", 0))
    with col2:
        st.metric("Total Comments", main_findings.get("total_comments", 0))
    with col3:
        st.metric("Posts With S1 Mentioned", main_findings.get("posts_with_s1_mentioned", 0))
    with col4:
        # Number of actionable items
        num_actionable = len(actionable_items)
        st.metric("Actionable Items", num_actionable)

    # S1 Sentiment Distribution (Bar or Pie)
    st.subheader("SentinelOne Sentiment Distribution")

    sentiment_dict = main_findings.get("s1_sentiment_distribution", {})
    if not sentiment_dict:
        st.write("No sentiment data available.")
    else:
        # Convert dict -> DataFrame for plotting
        df_sentiment = pd.DataFrame([
            {"Sentiment": k, "Count": v}
            for k, v in sentiment_dict.items()
        ])

        # Chart using Altair
        chart_sentiment = alt.Chart(df_sentiment).mark_bar().encode(
            x=alt.X("Sentiment", sort=None),
            y="Count",
            tooltip=["Sentiment", "Count"]
        ).properties(
            width=600,
            height=300
        )
        st.altair_chart(chart_sentiment, use_container_width=True)

    # Competitor Mentions
    st.subheader("Top Competitor Mentions")

    competitor_list = main_findings.get("competitors_mentioned_summary", [])
    if not competitor_list:
        st.write("No competitor mentions available.")
    else:
        # Convert list -> DataFrame
        df_comps = pd.DataFrame(competitor_list)  # columns: competitor, mentions
        # Let user select how many top competitors to see
        top_n = st.slider("Select how many top competitors to display:", 5, 30, 10)
        df_top_comps = df_comps.head(top_n)

        chart_comps = alt.Chart(df_top_comps).mark_bar().encode(
            x=alt.X("competitor", sort=None),
            y="mentions",
            tooltip=["competitor", "mentions"]
        ).properties(
            width=700,
            height=400
        )
        st.altair_chart(chart_comps, use_container_width=True)

    # Actionable Items Section
    st.header("Actionable Items")
    st.markdown(
        "These are posts or comments where `action_needed == 'yes'`. Each item includes a reason and a suggested response.")

    if num_actionable == 0:
        st.write("No actionable items found!")
    else:
        # Let user filter by post/comment type or search
        filter_type = st.selectbox("Filter by type:", ["All", "post", "comment"])
        search_author = st.text_input("Search by author (for comments only):", "").strip()

        # Build a simple table or expanders
        filtered_items = []

        for item in actionable_items:
            # If user selects "All", show everything
            # else show only if matches item["type"]
            if filter_type != "All" and item["type"] != filter_type:
                continue
            # If searching for author, only show if comment has matching author
            if search_author and item["type"] == "comment":
                if search_author.lower() not in item.get("author", "").lower():
                    continue

            filtered_items.append(item)

        if not filtered_items:
            st.write("No items match your current filters.")
        else:
            st.write(f"Showing {len(filtered_items)} actionable item(s).")

            # Display each item in an Expander
            for i, item in enumerate(filtered_items, start=1):
                # Build a title for the expander
                if item["type"] == "post":
                    expander_label = f"Post {item['post_id']} | Reason: {item['action_reason']}"
                else:
                    expander_label = f"Comment {item.get('comment_id', '')} on Post {item['post_id']} (by {item.get('author', '')})"

                with st.expander(expander_label):
                    st.write(f"**Action Reason:** {item['action_reason']}")
                    st.write(f"**Suggested Response:** {item['suggested_response']}")
                    if item["type"] == "post":
                        # If it's a post, we can also show the title
                        st.write(f"**Post Title:** {item.get('title', '')}")
                    else:
                        # If it's a comment, show the author
                        st.write(f"**Author:** {item.get('author', '')}")

    st.success("Dashboard loaded successfully.")


if __name__ == "__main__":
    main()
