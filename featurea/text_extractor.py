import requests
from google import genai
from google.genai import types
import os
from config import GEMINI_MODEL_NAME

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

def extract_text_from_url(
    image_url: str,
    prompt: str,
) -> str:
    """
    Extract OCR text from a single image URL using Gemini.
    """

    response_http = requests.get(image_url)
    response_http.raise_for_status()

    content_type = response_http.headers.get(
        "Content-Type",
        "image/jpeg",
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=response_http.content,
                mime_type=content_type,
            ),
        ],
    )

    return response.text

