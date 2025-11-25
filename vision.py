"""
Vision Module - Template Matching for Game UI Detection

Uses OpenCV template matching for fast, reliable detection of UI elements.
Works like smart_clicker.py - searches entire screenshot automatically.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


def check_template_in_image(
    image_path: str,
    template_path: str,
    confidence: float = 0.7,
    search_region: Optional[Tuple[int, int, int, int]] = None
) -> bool:
    """
    Check if a template image appears in the target image using OpenCV template matching.
    This is much faster and more reliable than LLM-based text detection for consistent UI elements.

    Works like smart_clicker.py - searches entire screenshot by default, no hardcoded regions needed!

    Args:
        image_path: Path to the screenshot/image to search in
        template_path: Path to the template image to look for
        confidence: Match confidence threshold (0.0 to 1.0). Default 0.7
        search_region: Optional (x, y, width, height) tuple to limit search area.
                      If None (default), searches entire image like smart_clicker.py.
                      Use for optimization only if needed.

    Returns:
        True if template is found with confidence >= threshold, False otherwise

    Example:
        >>> # Simple usage - searches entire screenshot
        >>> found = check_template_in_image(
        ...     "screenshot.png",
        ...     "resources/shoot_house_text.png",
        ...     confidence=0.8
        ... )
    """
    try:
        # Load the target image
        target_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if target_img is None:
            print(f"[ERROR] Failed to load image: {image_path}")
            return False

        # Load the template image
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"[ERROR] Failed to load template: {template_path}")
            return False

        # If search region is specified, crop the target image
        if search_region is not None:
            x, y, w, h = search_region
            target_img = target_img[y:y+h, x:x+w]

        # Get template dimensions
        template_height, template_width = template.shape[:2]
        target_height, target_width = target_img.shape[:2]

        # Check if template is larger than target
        if template_height > target_height or template_width > target_width:
            print(f"[WARNING] Template is larger than search area")
            return False

        # Perform template matching
        result = cv2.matchTemplate(target_img, template, cv2.TM_CCOEFF_NORMED)

        # Find the best match location
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Check if match confidence meets threshold
        match_found = max_val >= confidence

        if match_found:
            print(f"[SUCCESS] Template found! Confidence: {max_val:.2f} (threshold: {confidence:.2f})")
        else:
            print(f"[FAILED] Template not found. Best match: {max_val:.2f} (threshold: {confidence:.2f})")

        return match_found

    except Exception as e:
        print(f"[ERROR] Error during template matching: {e}")
        return False


def locate_template_in_image(
    image_path: str,
    template_path: str,
    confidence: float = 0.7,
    search_region: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Tuple[int, int, int, int]]:
    """
    Locate a template in an image and return its bounding box coordinates.

    Args:
        image_path: Path to the screenshot/image to search in
        template_path: Path to the template image to look for
        confidence: Match confidence threshold (0.0 to 1.0)
        search_region: Optional (x, y, width, height) tuple to limit search area

    Returns:
        Tuple[int, int, int, int]: (x, y, width, height) of the matched region,
                                   or None if not found
    """
    try:
        target_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if target_img is None:
            return None

        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None

        # Store original offset if using search region
        offset_x, offset_y = 0, 0

        if search_region is not None:
            x, y, w, h = search_region
            offset_x, offset_y = x, y
            target_img = target_img[y:y+h, x:x+w]

        template_height, template_width = template.shape[:2]

        result = cv2.matchTemplate(target_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            # Adjust coordinates if search region was used
            return (
                max_loc[0] + offset_x,
                max_loc[1] + offset_y,
                template_width,
                template_height
            )

        return None

    except Exception:
        return None
