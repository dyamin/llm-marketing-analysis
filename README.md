# Marketing Reddit Analysis

A Python-based tool to analyze SentinelOne (or any other solution) mentions and competitor discussions on the r/msp
subreddit, using the Reddit
API and Google's Gemini LLM.

## Project Overview

This 3-hour prototype analyzes Reddit discussions about SentinelOne and its competitors to provide actionable insights
for the marketing team. The analysis pipeline includes:

1. **Collect** data from Reddit’s /r/msp subreddit related to SentinelOne and its competitors,
2. **Process** that data with an LLM (Gemini or any other model) to extract key attributes (advantages, disadvantages,
   sentiment, etc.),
3. **Aggregate** the insights into an actionable analysis for the marketing team,
4. **Provide** an automated way to handle “actionable” feedback (e.g., how to respond to serious complaints or direct
   requests).
5. **Visualize** the final results in a Streamlit dashboard (bonus).

## Project Structure

```
marketing-analysis/
├── data/
│   ├── raw/              # Raw Reddit data
│   └── processed/        # Processed analysis results
├── src/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── logger.py             # Simple logger setup
│   │   └── constants.py          # Paths & shared constants
│   ├── data_analysis/
│   │   ├── __init__.py
│   │   ├── plotter.py            # Script to generate plots
│   │   └── dashboard.py          # Streamlit dashboard for visualization
│   ├── data_collection/
│   │   ├── __init__.py
│   │   └── fetch_data.py         # Script to collect Reddit data using PRAW
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── providers/
│   │   ├── __init__.py
│   │   │   ├── gemini.py         # Contains LLM calling logic & JSON parsing
│   │   ├── prompts.py            # Our LLM prompt templates
│   │   ├── pre_processor.py      # Main script to read raw data & call the LLM
│   │   └── post_processor.py     # Analysis script to aggregate and find actionable items
│   └── __init__.py
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Project overview

```

## Setup & Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=your_username
   REDDIT_PASSWORD=your_password
   REDDIT_USER_AGENT=script:sentinel-one-analysis:v1.0 (by /u/your_username)
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

1. **Collect Reddit Data**:
   ```bash
    python src/data_collection/fetch_data.py
    # produces msp_data.json
    ```

2. **Run LLM Processor**:
   ```bash
    python src/data_processing/pre_processor.py
    # produces msp_processed.json
    ```

3. **Aggregate & Analyze**:
   ```bash
    python src/data_processing/post_processor.py
    # produces analysis_results.json
   ```

4. **View Plots**:
   ```bash
    python src/data_analysis/plotter.py
    # produces plots in reports folder
   ```

5. **View Streamlit Dashboard**:
   ```bash
    streamlit run src/data_analysis/dashboard.py
    # open browser: http://localhost:8501
   ```

## Implementation Details

### Data Collection

**Goal**: Gather posts/comments from /r/msp referencing “SentinelOne” or competitor keywords.
**Implementation**:

- Uses PRAW with OAuth credentials (Reddit client ID & secret).
- Searches subreddit with queries like "SentinelOne OR S1" or for other competitor names.
- Fetches top-level posts, plus a subset of comments for each post.
- Saves results in JSON (e.g., msp_data.json).

### Content Analysis

**Goal**: Summarize each post/comment, classify sentiment toward S1, identify benefits/complaints, competitor mentions,
etc.
**Implementation**:

- We read msp_data.json.
- For each post & comment, we call a function like process_content_with_genai(text) which:
    - Builds a prompt from a template (see prompts.py).
    - Calls the Gemini API (or another LLM provider).
    - Parses the returned JSON, ensuring keys like "summary", "sentiment_s1", "competitors_mentioned", "
      action_needed", etc.
- Writes the enriched data as msp_processed.json.

### Post-Processing (Analysis)

**Goal**: Create final aggregates for the marketing team and a list of actionable items.
**Implementation**:

- Reads processed_msp_data.json.
- Tally:
    - Sentiment distribution (positive, negative, neutral, etc.) across all posts/comments,
    - Competitor mentions (count how often each competitor was named),
    - Actionable items (where the LLM identified "action_needed": "yes").
- Outputs an analysis_results.json containing:
    - "main_findings": Overall stats and competitor summary,
    - "actionable_items": Detailed reasons and suggested_response.

### Visualization

**Goal**: Provide a simple Streamlit UI to display the analysis.
**Implementation**:

- Run streamlit run src/data_analysis/dashboard.py.
- Shows KPIs (total posts, total comments, sentiment distribution) in a bar chart, competitor mentions bar chart, and an
  interactive table of actionable items.

## Example Findings

From the analyzed data:

- Total Posts: 41
- Total Comments: 325
- SentinelOne Mentions: 5
- Top Competitors:
    1. Huntress (18 mentions)
    2. Fortinet (7 mentions)
    3. Veeam (6 mentions)

## Major  Assumptions

1. LLM Provider: We used Gemini (but code could easily swap to OpenAI or another).
2. Prompt Format:
    - We prompt the LLM to return JSON with specific keys like summary, sentiment_s1, competitors_mentioned,
      action_needed,
      etc.
    - We strip triple-backticks if they appear to ensure valid JSON.
3. Actionable Criteria: If the LLM sets "action_needed": "yes", we treat it as actionable. One could also refine the
   logic or apply additional rules.
4. Rate Limiting: We added simple time.sleep(...) calls to stay within free-tier LLM or Reddit API rate limits.
5. Data Storage: We used JSON for both raw and processed data. (Could use CSV, or a DB, etc.)

## Next Steps

### 1. Data Collection Improvements

- Implement historical data collection
- Add continuous monitoring
- Expand to other relevant subreddits
- Add competitor keyword variations
- Implement data validation and cleaning

### 2. Analysis Enhancements

- Add topic modeling:
    - Let the LLM identify major “topics” (e.g., pricing, support, performance) for grouping beyond just
      “competitors_mentioned” or “sentiment_s1.”
- Implement trend analysis over time
- Add price sensitivity analysis
- Create competitor feature comparison matrix
- Add user sentiment change tracking

### 3. LLM Processing

- Better Prompt Engineering:
    - Add more robust instructions to handle edge cases, or use function calling / JSON schema constraints in a more
      advanced LLM framework.
- Add confidence scores for insights
- Sentiment Calibration:
    - LLM might produce “Positive” vs. “positive” vs. “mostly positive.” We can unify them or use a standard numeric
      scale.
- Implement alternative LLM providers

### 4. Dashboard & Visualization

- Add real-time data updates
- Create exportable reports
- Implement custom alert thresholds

### 5. Infrastructure & Performance

- Add data persistence layer
- Implement caching: implement a caching layer or a local DB so we don’t re-call the LLM for the same text multiple
  times.
- Add batch processing
- Improve error handling
- Add testing

### 6. Business Integration

- Auto-Reply / Engagement:
    - Potentially integrate a system to automatically respond in Reddit (with PRAW) or send an email/Slack message to
      marketing if “action_needed” is “yes.”
    - Combine with a “human approval” step so marketing can finalize the suggested response.
    - Add priority scoring for actions
- Possibly push final results to a CRM or marketing automation platform for follow-up.

## Limitations & Considerations

- Reddit API rate limits
- LLM processing costs
- Data freshness
- Limited scope of analysis

## Conclusion

Within >3 hours, we built a proof-of-concept pipeline that scrapes Reddit, uses an LLM to classify and summarize
mentions of SentinelOne, identifies competitor mentions, organizes final insights, and shows actionable items for the
marketing team.
The solution is easily extensible and showcases how you can combine NLP/LLM summarization with real-world data (Reddit)
to produce a valuable marketing analysis.
