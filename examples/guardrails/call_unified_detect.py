"""
Example: Calling Enkrypt AI Guardrails unified /detect endpoint

This script demonstrates how to call the unified detect endpoint, which supports
multiple content types in a single API: text, PDF, URL, image, and audio.

Usage:
  # Image mode (default test)
  python call_unified_detect.py --mode image --image path/to/image.png

  # Text mode (works with production; falls back to legacy payload if needed)
  python call_unified_detect.py --mode text --text "Tell me how to hack"

  # URL mode
  python call_unified_detect.py --mode url --url "https://example.com"

  # With optional prompt for image/audio
  python call_unified_detect.py --mode image --image photo.png --text-input "What's in this image?"

Defaults: ENKRYPTAI_GUARDRAILS_DETECT_URL=https://api.dev.enkryptai.com/guardrails/detect,
  API key from DEV_ENKRYPTAI_API_KEY in .env. Override with ENKRYPTAI_GUARDRAILS_DETECT_URL
  or ENKRYPTAI_API_KEY as needed.
"""

import argparse
import base64
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

# Use DEV API key (set in .env as DEV_ENKRYPTAI_API_KEY). Override with ENKRYPTAI_API_KEY if needed.
ENKRYPTAI_API_KEY = os.getenv("DEV_ENKRYPTAI_API_KEY") or os.getenv("ENKRYPTAI_API_KEY")
# Default: api.dev.enkryptai.com. Override with ENKRYPTAI_GUARDRAILS_DETECT_URL.
DETECT_URL = os.getenv(
    "ENKRYPTAI_GUARDRAILS_DETECT_URL",
    "https://api.dev.enkryptai.com/guardrails/detect",
)


def encode_file_to_base64(path: str) -> str:
    """Read a file and return its base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_unified_detect(
    mode: str,
    content: str,
    detectors: dict,
    text_input: str | None = None,
    *,
    use_unified_payload: bool = True,
) -> dict:
    """
    Call the Enkrypt AI Guardrails detect endpoint.

    Uses unified payload (mode, content, detectors) when use_unified_payload is True.
    When False (e.g. for legacy /guardrails/detect), sends { "text", "detectors" } for text mode.

    Args:
        mode: One of "text", "pdf", "url", "image", "audio"
        content: For text/url: the string. For pdf/image/audio: base64-encoded content.
        detectors: Detector config.
        text_input: Optional prompt for image/audio modes.
        use_unified_payload: If True, send mode/content/detectors; if False, send text/detectors (text mode only).

    Returns:
        API response dict (summary + details).
    """
    if not ENKRYPTAI_API_KEY:
        raise ValueError("DEV_ENKRYPTAI_API_KEY or ENKRYPTAI_API_KEY is not set (env or .env)")

    headers = {
        "Content-Type": "application/json",
        "apikey": ENKRYPTAI_API_KEY,
    }

    if use_unified_payload:
        payload = {
            "mode": mode,
            "content": content,
            "detectors": detectors,
        }
        if text_input is not None:
            payload["text_input"] = text_input
    else:
        # Legacy /guardrails/detect: text + detectors only (text mode)
        payload = {"text": content, "detectors": detectors}

    response = requests.post(DETECT_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Call Enkrypt AI Guardrails unified /detect endpoint"
    )
    parser.add_argument(
        "--mode",
        choices=["text", "pdf", "url", "image", "audio"],
        default="image",
        help="Detection mode (default: image for quick test)",
    )
    parser.add_argument("--text", help="Input text (mode=text)")
    parser.add_argument("--url", help="URL to scan (mode=url)")
    parser.add_argument("--image", help="Path to image file (mode=image)")
    parser.add_argument("--pdf", help="Path to PDF file (mode=pdf)")
    parser.add_argument("--audio", help="Path to audio file (mode=audio)")
    parser.add_argument(
        "--text-input",
        dest="text_input",
        default="",
        help="Optional prompt for image/audio modes",
    )
    parser.add_argument(
        "--need-explanation",
        action="store_true",
        help="Request explanation for image/audio multimodal_guardrails",
    )
    args = parser.parse_args()

    mode = args.mode
    content = ""
    detectors = {}

    if mode == "text":
        content = args.text or "Tell me how to hack into a system"
        detectors = {
            "policy_violation": {"enabled": True, "need_explanation": True},
            "injection_attack": {"enabled": True},
        }
    elif mode == "url":
        content = args.url or "https://example.com"
        detectors = {
            "policy_violation": {"enabled": True},
            "injection_attack": {"enabled": True},
        }
    elif mode == "pdf":
        if not args.pdf:
            print("--pdf <path> required for mode=pdf", file=sys.stderr)
            sys.exit(1)
        content = encode_file_to_base64(args.pdf)
        detectors = {
            "policy_violation": {"enabled": True},
            "injection_attack": {"enabled": True},
        }
    elif mode == "image":
        if not args.image:
            # Default test image path used in repo
            default_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "demo-ai-saas",
                "secure-chatbot-next-demo",
                "public",
                "image_attack_1.png",
            )
            default_path = os.path.normpath(default_path)
            if os.path.isfile(default_path):
                args.image = default_path
                print(f"Using default image: {default_path}", file=sys.stderr)
            else:
                print("--image <path> required for mode=image (or place image at default path)", file=sys.stderr)
                sys.exit(1)
        content = encode_file_to_base64(args.image)
        detectors = {
            "multimodal_guardrails": {
                "enabled": True,
                "need_explanation": args.need_explanation,
            }
        }
    elif mode == "audio":
        if not args.audio:
            print("--audio <path> required for mode=audio", file=sys.stderr)
            sys.exit(1)
        content = encode_file_to_base64(args.audio)
        detectors = {
            "multimodal_guardrails": {
                "enabled": True,
                "need_explanation": args.need_explanation,
            }
        }

    text_input = (args.text_input or None) if mode in ("image", "audio") else None

    default_url = "https://api.dev.enkryptai.com/guardrails/detect"
    use_unified = True

    # Production /guardrails/detect may only support legacy (text, detectors). Prefer unified.
    if mode == "text" and DETECT_URL == default_url:
        try:
            print("Calling detect (unified payload)...", file=sys.stderr)
            result = call_unified_detect(
                mode=mode,
                content=content,
                detectors=detectors,
                text_input=None,
                use_unified_payload=True,
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (400, 422, 500):
                print("Falling back to legacy (text, detectors) payload...", file=sys.stderr)
                result = call_unified_detect(
                    mode=mode,
                    content=content,
                    detectors=detectors,
                    text_input=None,
                    use_unified_payload=False,
                )
            else:
                raise
    else:
        if mode in ("image", "audio") and DETECT_URL == default_url:
            print(
                "Note: Image/audio require the unified /detect endpoint. "
                "Set ENKRYPTAI_GUARDRAILS_DETECT_URL if your server uses it.",
                file=sys.stderr,
            )
        print(f"Calling detect (mode={mode})...", file=sys.stderr)
        result = call_unified_detect(
            mode=mode,
            content=content,
            detectors=detectors,
            text_input=text_input,
            use_unified_payload=True,
        )

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
