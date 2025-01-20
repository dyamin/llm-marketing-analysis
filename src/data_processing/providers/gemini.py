import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.common.logger import get_logger
from src.data_processing.prompts import SUMMARIZATION_TEMPLATE

load_dotenv()

logger = get_logger(__name__)

DEFAULT_MODEL = "gemini-1.5-flash"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def process_content_with_genai(post_text: str) -> dict:
    """
    Calls the Google Gen AI (Gemini) SDK to summarize & classify a post.
    Returns a dict with the parsed JSON fields (e.g. summary, sentiment_s1, etc.).
    """
    llm_output = ""

    # Basic truncation in case the post is very long
    max_length = 2000
    truncated_text = post_text[:max_length]

    prompt = SUMMARIZATION_TEMPLATE.format(text=truncated_text)

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=400
            ),
        )
        llm_output = response.text
        # Remove ```json fences if present
        clean_output = strip_markdown_code_fences(llm_output)

        parsed_response = json.loads(clean_output)
        if not parsed_response:
            logger.error(f"Gemini response was not valid JSON. Output:\n{response.text}")
            return get_default_response()

        return parsed_response

    except json.JSONDecodeError:
        logger.error("Gemini response was not valid JSON. Output:\n" + llm_output)
        return get_default_response()
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        return get_default_response()


def get_default_response() -> dict:
    """Return a default response structure."""
    return {
        "summary": "",
        "sentiment_s1": "unknown",
        "benefits_mentioned": [],
        "complaints_mentioned": [],
        "competitors_mentioned": [],
        "overall_tone": "unknown",
        "action_needed": "no_action",
        "action_reason": "",
        "suggested_response": ""
    }


def strip_markdown_code_fences(text: str) -> str:
    """
    If the text is wrapped in triple-backtick fences, remove them so it's valid JSON.
    e.g.:
        ```json
        { "summary": "..." }
        ```
    becomes
        { "summary": "..." }
    """
    # Remove leading fences like ``` or ```json
    text = re.sub(r"^```(\w+)?", "", text.strip())
    # Remove trailing fences
    text = re.sub(r"```$", "", text.strip())
    return text.strip()
