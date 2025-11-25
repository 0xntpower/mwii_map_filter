"""
Ollama LLM Vision Utilities

UNUSED - Legacy code for LLM-based text detection.
Template matching is now used instead (faster and more reliable).

This module is kept for reference but is not used in production.
"""

from pathlib import Path
import base64
import re
import requests

LLM_FOR_VISION = "llava:7b"


def check_text_in_image(image_path: str, text_to_find: str = "Black Gold",
                        model: str = LLM_FOR_VISION,
                        host: str = "http://localhost:11434") -> bool:
    """
    Check if specific text appears in an image using Ollama vision model.

    DEPRECATED: Use check_template_in_image() from vision.py instead.
    This LLM-based approach is slow and unreliable compared to template matching.

    Args:
        image_path: Path to the image file
        text_to_find: Text to look for (default: "Black Gold")
        model: Ollama vision model to use
        host: Ollama server URL

    Returns:
        True if text is found, False otherwise
    """
    url = f"{host}/api/generate"

    # Read and encode image to base64
    try:
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"[ERROR] Image not found: {image_path}")
        return False

    # Craft a prompt that encourages yes/no answer
    prompt = f"""Look at this image carefully. The image shows a computer screen with a game interface, within the game UI can you Can you see the text "{text_to_find}" at least two of the words anywhere in the image? Consider that it might be with a different font and color if yes say where in the picture you see it"""

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.1,  # Very low for consistent answers
            "num_predict": 10    # Limit response length
        }
    }

    try:
        print(f"[CHECKING] Checking for '{text_to_find}' in image...")
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()

        response_text = r.json().get("response", "").strip().lower()
        print(f"[RESPONSE] Model response: {response_text}")

        # Parse response to boolean
        result = parse_yes_no_response(response_text)
        print(f"[RESULT] Result: {result}")

        return result

    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return False


def parse_yes_no_response(response: str) -> bool:
    """
    Parse various yes/no responses into boolean.
    Handles: yes, no, true, false, y, n, 1, 0, etc.
    """
    response = response.lower().strip()

    # Remove common punctuation
    response = re.sub(r'[.,!?;:]', '', response)

    # Check for positive responses
    positive_patterns = [
        r'\byes\b',
        r'\btrue\b',
        r'\b1\b',
        r'^y$',
        r'\baffirmative\b',
        r'\bcorrect\b',
        r'\bfound\b',
        r'\bvisible\b',
        r'\bcan see\b',
        r'\bi see\b',
    ]

    for pattern in positive_patterns:
        if re.search(pattern, response):
            return True

    # Check for negative responses
    negative_patterns = [
        r'\bno\b',
        r'\bfalse\b',
        r'\b0\b',
        r'^n$',
        r'\bnegative\b',
        r'\bincorrect\b',
        r'\bnot found\b',
        r'\bnot visible\b',
        r'\bcannot see\b',
        r'\bcan\'t see\b',
        r'\bdon\'t see\b',
    ]

    for pattern in negative_patterns:
        if re.search(pattern, response):
            return False

    # Default to False if unclear
    print(f"[WARNING] Unclear response, defaulting to False")
    return False


if __name__ == "__main__":
    print("="*70)
    print("OLLAMA VISION UTILITIES (UNUSED)")
    print("="*70)
    print("\nThis module contains legacy LLM-based text detection code.")
    print("It is no longer used in production.")
    print("\nUse vision.check_template_in_image() instead for:")
    print("  - Faster detection (<0.1s vs 2-5s)")
    print("  - More reliable (no false positives)")
    print("  - No external API calls needed")
    print("="*70)
