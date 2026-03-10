"""
Example: Calling Enkrypt AI Image Guardrails with a Sample Policy Document

This script demonstrates how to use Enkrypt AI's image guardrails API
to detect policy violations, toxicity, NSFW content, injection attacks,
and PII in images -- using the Generic Legal AI Policy as the policy text.
"""

import os
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

ENKRYPTAI_API_KEY = os.getenv("ENKRYPTAI_API_KEY")

POLICY_TEXT = "No cats allowed."

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "images", "cat.jpg")


def image_file_to_base64(path):
    """Read a local image file and return its base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_image_guardrails(text_input, image_data, policy_text):
    """
    Call the Enkrypt AI image guardrails API with all detectors enabled.

    Args:
        text_input: Text prompt accompanying the image
        image_data: Image URL or base64-encoded image data
        policy_text: Custom policy text for policy violation detection

    Returns:
        dict: JSON response from the API
    """
    url = "https://api.enkryptai.com/guardrails/detect-image"

    payload = {
        "text_input": text_input,
        "image_data": image_data,
        "detectors": {
            "toxicity": {"enabled": False},
            "nsfw": {"enabled": False},
            "injection_attack": {"enabled": True},
            "pii": {
                "enabled": True,
                "entities": ["person", "phone", "email"]
            },
            "policy_violation": {
                "enabled": True,
                "policy_text": policy_text,
                "need_explanation": True
            }
        }
    }

    headers = {
        "apikey": ENKRYPTAI_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    text_input = "Review this image for policy compliance."
    image_path = os.path.abspath(IMAGE_PATH)

    print("Calling Enkrypt AI Image Guardrails...")
    print(f"  Text input: {text_input}")
    print(f"  Image: {image_path}")
    print(f"  Policy: {POLICY_TEXT}")
    print()

    image_b64 = image_file_to_base64(image_path)
    print(f"  Encoded image size: {len(image_b64)} chars")
    print()

    result = call_image_guardrails(
        text_input=text_input,
        image_data=image_b64,
        policy_text=POLICY_TEXT,
    )

    print("Response:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
