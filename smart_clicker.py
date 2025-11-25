"""
Smart Click Button - UI Automation Utility
Locates and clicks buttons in any window (including fullscreen applications) using image recognition.
"""

import pyautogui
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import random
import time
import math


class ButtonNotFoundException(Exception):
    """Raised when the target button cannot be found on screen."""
    pass


def _human_bezier_curve(start: Tuple[int, int], end: Tuple[int, int]) -> list:
    """
    Generate a smooth bezier curve path between two points.
    Returns fewer waypoints - PyAutoGUI will interpolate smoothly between them.
    
    Creates unique patterns each time by varying:
    - Number of control points (1-3)
    - Curvature intensity
    - Path complexity
    """
    # Randomize the number of control points for pattern variation
    control_points = random.randint(1, 3)
    
    # Calculate distance for adaptive curvature
    distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
    
    # Vary curvature intensity - sometimes straighter, sometimes more curved
    curvature_factor = random.uniform(0.3, 1.0)
    
    # Generate random control points for the curve
    control = []
    for i in range(control_points):
        # Progress ratio for this control point
        progress = (i + 1) / (control_points + 1)
        
        # Interpolate between start and end
        base_x = int(start[0] + (end[0] - start[0]) * progress)
        base_y = int(start[1] + (end[1] - start[1]) * progress)
        
        # Add random offset with variable intensity
        # Sometimes more arc, sometimes less
        base_offset = min(120, distance // 4)
        offset_range = int(base_offset * curvature_factor)
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        
        control.append((base_x + offset_x, base_y + offset_y))
    
    # Add start and end to control points
    all_points = [start] + control + [end]
    
    # Vary number of waypoints for different movement personalities
    # Sometimes smoother (fewer points), sometimes more detailed
    steps = random.randint(3, 7)
    
    points = []
    for i in range(steps + 1):
        t = i / steps
        x, y = _bezier_point(all_points, t)
        points.append((int(x), int(y)))
    
    return points


def _bezier_point(points: list, t: float) -> Tuple[float, float]:
    """Calculate a point on bezier curve at time t."""
    n = len(points) - 1
    x = sum(points[i][0] * _bernstein(n, i, t) for i in range(n + 1))
    y = sum(points[i][1] * _bernstein(n, i, t) for i in range(n + 1))
    return x, y


def _bernstein(n: int, i: int, t: float) -> float:
    """Bernstein polynomial for bezier curves."""
    from math import comb
    return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))


def _human_mouse_move(target_x: int, target_y: int, 
                      duration: Optional[float] = None,
                      overshoot: bool = True) -> None:
    """
    Move mouse to target with human-like characteristics.
    
    Creates unique movement patterns by varying:
    - Movement speed personality
    - Easing functions
    - Overshoot behavior
    - Mid-movement micro-pauses
    
    Args:
        target_x, target_y: Destination coordinates
        duration: Movement duration (randomized if None)
        overshoot: Whether to slightly overshoot then correct
    """
    start_x, start_y = pyautogui.position()
    
    # Small pre-movement adjustment (humans sometimes micro-adjust before big moves)
    if random.random() > 0.7:  # 30% chance
        pre_adjust_x = start_x + random.randint(-3, 3)
        pre_adjust_y = start_y + random.randint(-3, 3)
        pyautogui.moveTo(pre_adjust_x, pre_adjust_y, duration=random.uniform(0.05, 0.1))
        time.sleep(random.uniform(0.01, 0.03))
        start_x, start_y = pyautogui.position()
    
    # Calculate distance for adaptive duration
    distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
    
    # Randomize movement duration with more personality variation
    if duration is None:
        # Base duration with more human-like variation
        base_duration = min(0.5 + (distance / 1500), 2.0)
        
        # Add "personality" - sometimes faster, sometimes more cautious
        personality = random.choice([
            ('fast', 0.7, 0.9),      # Quick mover
            ('normal', 0.85, 1.15),   # Average speed
            ('careful', 1.1, 1.3),    # More deliberate
        ])
        duration = base_duration * random.uniform(personality[1], personality[2])
    
    # Randomize overshoot behavior for variety
    overshoot_chance = random.uniform(0.2, 0.5)  # 20-50% chance
    overshoot_amount = random.randint(2, 5)       # Variable overshoot distance
    
    # Add slight overshoot for realism (humans don't move perfectly)
    if overshoot and random.random() > overshoot_chance:
        overshoot_x = target_x + random.randint(-overshoot_amount, overshoot_amount)
        overshoot_y = target_y + random.randint(-overshoot_amount, overshoot_amount)
        
        # Move to overshoot position with smooth bezier curve
        path = _human_bezier_curve((start_x, start_y), (overshoot_x, overshoot_y))
        _smooth_move_along_path(path, duration * random.uniform(0.85, 0.95))
        
        # Correct to actual target with variable correction time
        correction_duration = random.uniform(0.04, 0.15)
        # Sometimes use different easing for correction
        correction_tween = random.choice([
            pyautogui.easeOutQuad,
            pyautogui.easeOutCubic,
        ])
        pyautogui.moveTo(target_x, target_y, duration=correction_duration, tween=correction_tween)
    else:
        # Direct movement with curve
        path = _human_bezier_curve((start_x, start_y), (target_x, target_y))
        _smooth_move_along_path(path, duration)
    
    # Occasional post-movement micro-adjustment (fine-tuning position)
    if random.random() > 0.8:  # 20% chance
        time.sleep(random.uniform(0.02, 0.05))
        adjust_x = target_x + random.randint(-1, 1)
        adjust_y = target_y + random.randint(-1, 1)
        if (adjust_x, adjust_y) != (target_x, target_y):
            pyautogui.moveTo(adjust_x, adjust_y, duration=random.uniform(0.03, 0.08))


def _smooth_move_along_path(path: list, duration: float) -> None:
    """
    Smoothly move mouse along a path of waypoints.
    Uses fewer waypoints with longer durations for ultra-smooth movement.
    PyAutoGUI handles the interpolation between waypoints.
    
    Adds variety through:
    - Different easing functions
    - Occasional micro-pauses
    - Variable segment timing
    """
    if len(path) < 2:
        return
    
    # Calculate time per segment with slight randomization
    base_time_per_segment = duration / (len(path) - 1)
    
    # Choose easing function with weighted randomness
    # More common: easeInOutQuad (smooth and natural)
    # Less common: others for variety
    tween_choices = [
        (pyautogui.easeInOutQuad, 0.6),   # 60% - Most common, very smooth
        (pyautogui.easeInOutCubic, 0.2),  # 20% - Even smoother
        (pyautogui.easeOutQuad, 0.15),    # 15% - Quick deceleration
        (pyautogui.easeInQuad, 0.05),     # 5% - Quick acceleration
    ]
    
    # Weighted random selection
    rand = random.random()
    cumulative = 0
    selected_tween = pyautogui.easeInOutQuad
    for tween, weight in tween_choices:
        cumulative += weight
        if rand <= cumulative:
            selected_tween = tween
            break
    
    # Move through each waypoint
    for i in range(1, len(path)):
        x, y = path[i]
        
        # Vary segment duration slightly for natural rhythm
        segment_duration = base_time_per_segment * random.uniform(0.85, 1.15)
        
        # Let PyAutoGUI smoothly move to each waypoint
        pyautogui.moveTo(x, y, duration=segment_duration, tween=selected_tween)
        
        # Occasional micro-pause mid-movement (humans sometimes hesitate briefly)
        # More likely in longer movements
        if i < len(path) - 1 and random.random() > 0.85:  # 15% chance
            time.sleep(random.uniform(0.01, 0.04))


def _human_click(x: int, y: int, button: str = 'left', clicks: int = 1,
                 interval: float = 0.0) -> None:
    """
    Perform a human-like click with randomized timing.
    
    Adds natural variation to:
    - Mouse down duration (variable per click)
    - Interval between clicks (variable)
    - Slight position jitter during click
    - Pre-click micro-adjustments
    """
    for i in range(clicks):
        if i > 0:
            # Randomize interval between clicks with more variation
            base_interval = interval if interval > 0 else 0.1
            actual_interval = base_interval * random.uniform(0.7, 1.4)
            time.sleep(max(0, actual_interval))
        
        # Small random jitter (humans don't click at exact pixel)
        jitter_amount = random.randint(1, 3)  # Variable jitter
        jitter_x = x + random.randint(-jitter_amount, jitter_amount)
        jitter_y = y + random.randint(-jitter_amount, jitter_amount)
        
        # Move to click position if not already there
        current_x, current_y = pyautogui.position()
        if abs(current_x - jitter_x) > 1 or abs(current_y - jitter_y) > 1:
            # Small adjustment to final position
            pyautogui.moveTo(jitter_x, jitter_y, duration=random.uniform(0.01, 0.03))
        
        # Variable pre-click pause (humans don't click instantly upon arrival)
        time.sleep(random.uniform(0.01, 0.05))
        
        # Randomize mouse down/up timing with more personality variation
        # Sometimes quick, sometimes more deliberate
        click_speed = random.choice([
            ('quick', 0.04, 0.08),      # Fast clicker
            ('normal', 0.06, 0.12),     # Average
            ('deliberate', 0.10, 0.18), # Careful/precise
        ])
        mouse_down_duration = random.uniform(click_speed[1], click_speed[2])
        
        # Perform click with human timing
        if button == 'left':
            pyautogui.mouseDown(button='left')
        elif button == 'right':
            pyautogui.mouseDown(button='right')
        elif button == 'middle':
            pyautogui.mouseDown(button='middle')
        
        time.sleep(mouse_down_duration)
        
        if button == 'left':
            pyautogui.mouseUp(button='left')
        elif button == 'right':
            pyautogui.mouseUp(button='right')
        elif button == 'middle':
            pyautogui.mouseUp(button='middle')
        
        # Variable pause after click
        time.sleep(random.uniform(0.01, 0.04))


def smart_click_button(
    target_image_path: str,
    confidence: float = 0.8,
    click_offset: Tuple[int, int] = (0, 0),
    button: str = 'left',
    clicks: int = 1,
    interval: float = 0.0,
    pause_after: float = 0.5,
    human_like: bool = True,
    pre_move_delay: Optional[Tuple[float, float]] = None
) -> Tuple[int, int]:
    """
    Locate and click a button on screen using image recognition.
    
    This function works with any UI element, including those in fullscreen applications
    and games. It uses template matching to find the target button and clicks it.
    
    Args:
        target_image_path: Path to the PNG image of the button to click
        confidence: Match confidence threshold (0.0 to 1.0). Higher = stricter matching.
                   Default 0.8 works well for most cases.
        click_offset: Tuple (x, y) offset from center of found image. 
                     Use this if you need to click slightly offset from center.
        button: Mouse button to click - 'left', 'right', or 'middle'
        clicks: Number of clicks to perform
        interval: Interval between clicks in seconds
        pause_after: Pause duration after clicking (default 0.5s)
        human_like: Enable human-like mouse movement and click timing (default True).
                   When enabled, adds:
                   - Bezier curve mouse movements
                   - Random timing variations
                   - Slight overshooting/correction
                   - Randomized mouse down/up timing
        pre_move_delay: Optional (min, max) tuple for random delay before moving mouse.
                       Example: (0.1, 0.3) adds 100-300ms delay before action.
                       Useful for appearing more natural.
    
    Returns:
        Tuple[int, int]: The (x, y) coordinates where the click occurred
    
    Raises:
        FileNotFoundError: If the target image file doesn't exist
        ButtonNotFoundException: If the button cannot be found on screen
        
    Example:
        >>> # Simple usage with human-like behavior (default)
        >>> smart_click_button("button.png")
        
        >>> # Instant/robotic clicking (for speed)
        >>> smart_click_button("submit_btn.png", human_like=False)
        
        >>> # With pre-action delay for extra realism
        >>> smart_click_button("play.png", pre_move_delay=(0.2, 0.5))
        
        >>> # Right-click with offset and human behavior
        >>> smart_click_button("context_menu.png", button='right', click_offset=(10, 5))
    """
    # Validate target image path
    target_path = Path(target_image_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Target image not found: {target_image_path}")
    
    # Load the target image (template)
    template = cv2.imread(str(target_path), cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"Failed to load image: {target_image_path}")
    
    template_height, template_width = template.shape[:2]
    
    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Perform template matching
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    
    # Find the best match location
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Check if match confidence meets threshold
    if max_val < confidence:
        raise ButtonNotFoundException(
            f"Button not found on screen. "
            f"Best match confidence: {max_val:.2f}, required: {confidence:.2f}. "
            f"Try lowering the confidence threshold or ensure the button is visible."
        )
    
    # Calculate center point of the matched region
    center_x = max_loc[0] + template_width // 2 + click_offset[0]
    center_y = max_loc[1] + template_height // 2 + click_offset[1]
    
    # Optional pre-movement delay for realism
    if pre_move_delay is not None:
        delay = random.uniform(pre_move_delay[0], pre_move_delay[1])
        time.sleep(delay)
    
    # Perform the click with or without human-like behavior
    if human_like:
        # Move mouse with human-like bezier curve
        _human_mouse_move(center_x, center_y)
        
        # Click with randomized timing
        _human_click(center_x, center_y, button=button, clicks=clicks, interval=interval)
    else:
        # Direct robotic movement and click
        pyautogui.click(
            x=center_x,
            y=center_y,
            clicks=clicks,
            interval=interval,
            button=button
        )
    
    # Randomize pause after clicking if in human mode
    if human_like and pause_after > 0:
        # More human-like variation in post-click pause
        # Sometimes quick recovery, sometimes more deliberate
        pause_variation = random.uniform(0.7, 1.4)
        actual_pause = pause_after * pause_variation
        time.sleep(actual_pause)
    elif pause_after > 0:
        time.sleep(pause_after)
    
    return (center_x, center_y)


def locate_button(
    target_image_path: str,
    confidence: float = 0.8
) -> Optional[Tuple[int, int, int, int]]:
    """
    Locate a button on screen without clicking it.
    
    Args:
        target_image_path: Path to the PNG image of the button
        confidence: Match confidence threshold (0.0 to 1.0)
    
    Returns:
        Optional[Tuple[int, int, int, int]]: (x, y, width, height) of the button,
                                             or None if not found
                                             
    Example:
        >>> coords = locate_button("button.png")
        >>> if coords:
        >>>     print(f"Button found at: {coords}")
        >>> else:
        >>>     print("Button not found")
    """
    try:
        target_path = Path(target_image_path)
        if not target_path.exists():
            return None
        
        template = cv2.imread(str(target_path), cv2.IMREAD_COLOR)
        if template is None:
            return None
        
        template_height, template_width = template.shape[:2]
        
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            return (max_loc[0], max_loc[1], template_width, template_height)
        
        return None
        
    except Exception:
        return None


def wait_for_button(
    target_image_path: str,
    timeout: float = 10.0,
    confidence: float = 0.8,
    check_interval: float = 0.5
) -> bool:
    """
    Wait for a button to appear on screen.
    
    Args:
        target_image_path: Path to the PNG image of the button
        timeout: Maximum time to wait in seconds
        confidence: Match confidence threshold
        check_interval: Time between checks in seconds
    
    Returns:
        bool: True if button was found within timeout, False otherwise
        
    Example:
        >>> if wait_for_button("loading_complete.png", timeout=30):
        >>>     smart_click_button("next_button.png")
    """
    import time
    
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        if locate_button(target_image_path, confidence) is not None:
            return True
        time.sleep(check_interval)
    
    return False


def random_idle_movement(
    movement_range: int = 100,
    duration: float = 0.5,
    small_adjustments: int = 3
) -> None:
    """
    Perform random small mouse movements to simulate idle human behavior.
    
    This can help avoid detection systems that flag perfectly still cursors
    between actions. Simulates natural micro-adjustments and fidgeting.
    Now with more varied movement patterns.
    
    Args:
        movement_range: Maximum pixels to move from current position
        duration: How long the idle movement sequence should take
        small_adjustments: Number of small movements to make
        
    Example:
        >>> # Add idle movement between clicks
        >>> smart_click_button("button1.png")
        >>> random_idle_movement()
        >>> smart_click_button("button2.png")
    """
    current_x, current_y = pyautogui.position()
    
    # Vary the movement style
    movement_style = random.choice(['circular', 'linear', 'random'])
    
    if movement_style == 'circular':
        # Small circular motion (like user thinking)
        radius = movement_range // 2
        steps = small_adjustments + random.randint(2, 4)
        for i in range(steps):
            angle = (i / steps) * 2 * math.pi
            offset_x = int(radius * math.cos(angle))
            offset_y = int(radius * math.sin(angle))
            
            target_x = current_x + offset_x
            target_y = current_y + offset_y
            
            pyautogui.moveTo(target_x, target_y, 
                           duration=duration / steps,
                           tween=pyautogui.easeInOutQuad)
            time.sleep(random.uniform(0.05, 0.15))
            
    elif movement_style == 'linear':
        # Back and forth motion (like reading)
        for i in range(small_adjustments):
            direction = 1 if i % 2 == 0 else -1
            offset_x = random.randint(movement_range // 4, movement_range) * direction
            offset_y = random.randint(-movement_range // 4, movement_range // 4)
            
            target_x = current_x + offset_x
            target_y = current_y + offset_y
            
            _human_mouse_move(target_x, target_y, 
                            duration=duration / small_adjustments,
                            overshoot=False)
            time.sleep(random.uniform(0.1, 0.3))
            
    else:  # 'random'
        # Random small movements
        for _ in range(small_adjustments):
            # Variable offset with different intensities
            intensity = random.uniform(0.3, 1.0)
            offset_x = random.randint(-movement_range, movement_range) * intensity
            offset_y = random.randint(-movement_range, movement_range) * intensity
            
            target_x = int(current_x + offset_x)
            target_y = int(current_y + offset_y)
            
            # Use human-like movement
            _human_mouse_move(target_x, target_y, 
                            duration=duration / small_adjustments,
                            overshoot=False)
            
            # Variable pause between micro-movements
            time.sleep(random.uniform(0.08, 0.35))


def random_pause(
    min_seconds: float = 0.5,
    max_seconds: float = 2.0,
    with_movement: bool = False
) -> None:
    """
    Add a random pause with optional idle mouse movement.
    
    Simulates human thinking/reading time between actions.
    Now with more natural variation in timing and movement patterns.
    
    Args:
        min_seconds: Minimum pause duration
        max_seconds: Maximum pause duration
        with_movement: Whether to add small mouse movements during pause
        
    Example:
        >>> smart_click_button("read_article.png")
        >>> random_pause(2.0, 5.0, with_movement=True)  # Simulate reading
        >>> smart_click_button("next_page.png")
    """
    pause_duration = random.uniform(min_seconds, max_seconds)
    
    if with_movement:
        # Vary the number of movements during pause
        num_movements = random.randint(1, 4)
        
        # Sometimes cluster movements at start, sometimes spread evenly
        movement_pattern = random.choice(['early', 'spread', 'late'])
        
        if movement_pattern == 'early':
            # More movement at the start (user looking around)
            for i in range(num_movements):
                if i < num_movements * 0.6:
                    time.sleep(pause_duration * random.uniform(0.05, 0.15))
                    random_idle_movement(movement_range=random.randint(40, 80), 
                                       duration=random.uniform(0.2, 0.5),
                                       small_adjustments=1)
                else:
                    time.sleep(pause_duration * random.uniform(0.15, 0.25))
            time.sleep(pause_duration * 0.3)
            
        elif movement_pattern == 'spread':
            # Evenly distributed movements
            movement_interval = pause_duration / (num_movements + 1)
            for _ in range(num_movements):
                time.sleep(movement_interval * random.uniform(0.7, 1.3))
                random_idle_movement(movement_range=random.randint(30, 100), 
                                   duration=random.uniform(0.2, 0.4),
                                   small_adjustments=random.randint(1, 2))
            time.sleep(movement_interval * random.uniform(0.7, 1.3))
            
        else:  # 'late'
            # Movement towards the end (user getting ready to act)
            time.sleep(pause_duration * random.uniform(0.5, 0.7))
            for _ in range(num_movements):
                random_idle_movement(movement_range=random.randint(20, 60),
                                   duration=random.uniform(0.1, 0.3),
                                   small_adjustments=1)
                time.sleep(pause_duration * random.uniform(0.05, 0.1))
    else:
        time.sleep(pause_duration)


if __name__ == "__main__":
    # Example usage and testing
    print("Smart Clicker Utility - Enhanced with Human-like Behavior")
    print("=" * 60)
    print("\nThis module provides UI automation with natural human simulation.")
    print("\n📋 BASIC USAGE:")
    print("""
from smart_clicker import smart_click_button

# Simple click with human-like behavior (default)
smart_click_button("target.png")

# Fast/robotic clicking (no humanization)
smart_click_button("target.png", human_like=False)
    """)
    
    print("\n🎯 HUMANIZATION FEATURES:")
    print("""
# Add pre-action delay (thinking time)
smart_click_button("button.png", pre_move_delay=(0.2, 0.5))

# Add idle movements between actions
from smart_clicker import random_idle_movement, random_pause

smart_click_button("option1.png")
random_idle_movement()  # Simulate natural fidgeting
smart_click_button("option2.png")

# Simulate reading/thinking time with movements
smart_click_button("article.png")
random_pause(2.0, 5.0, with_movement=True)
smart_click_button("next.png")
    """)
    
    print("\n⚙️ WHAT GETS RANDOMIZED:")
    print("""
When human_like=True (default), the following are randomized:
  • Mouse movement path (bezier curves, not straight lines)
  • Movement speed based on distance
  • Slight overshoot with correction
  • Mouse down/up timing (50-150ms variation)
  • Click position jitter (±2 pixels)
  • Pause durations (±20% variation)
  • Pre-action delays
    """)
    
    print("\n🔒 RESPONSIBLE USE:")
    print("""
This tool is designed for:
  ✓ Legitimate automation testing
  ✓ Personal productivity scripts
  ✓ Accessibility assistance
  ✓ Development and debugging

Please ensure your use complies with:
  • Terms of service of applications
  • Local laws and regulations
  • Ethical automation practices
    """)
    
    print("\n📦 Required dependencies:")
    print("  pip install pyautogui opencv-python numpy")
    print("\n" + "=" * 60)