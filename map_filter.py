from smart_clicker import ButtonNotFoundException, smart_click_button
from vision import check_template_in_image
from sys import exit
from notify import send_windows_notification
from pyautogui import screenshot
from os import path, makedirs, remove
from datetime import datetime
from time import sleep

SCRIPT_DIR = path.dirname(path.abspath(__file__))

STARTING_DELAY_SECONDS = 5
SCREENSHOTS_DIR = path.join(SCRIPT_DIR, "screenshots")
RESOURCES_DIR = path.join(SCRIPT_DIR, "resources", "mwii")
IMAGE_EXIT_QUEUE_BUTTON = path.join(RESOURCES_DIR, "exit_queue_button.png")
IMAGE_JOIN_QUEUE_BUTTON = path.join(RESOURCES_DIR, "join_queue_button.png")
IMAGE_YES_QUIT_GREEN_BUTTON = path.join(RESOURCES_DIR, "yes_quit_green_template.png")
IMAGE_YES_QUIT_GREY_BUTTON = path.join(RESOURCES_DIR, "yes_quit_grey_template.png")
TEMPLATE_SEARCHING_FOR = path.join(RESOURCES_DIR, "searching_for_match_text.png")
TEMPLATE_SHOOT_HOUSE = path.join(RESOURCES_DIR, "shoothouse_template.png")

def click_target_element(btn_png_path: str) -> None:
    try:
        x, y = smart_click_button(btn_png_path)
        print(f"Successfully clicked button at ({x}, {y})")
    except ButtonNotFoundException:
         print("Button not found on screen")
    except FileNotFoundError:
        print("Target image file not found")

def capture_screen(save_dir: str = ".", filename: str = None) -> str:
    """
    Take a screenshot of the current display and return the file path.

    Args:
        save_dir: Directory to save screenshot (default: current directory)
        filename: Custom filename (default: auto-generated with timestamp)

    Returns:
        str: Full path to the saved PNG file
    """
    makedirs(save_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"screenshot_{timestamp}.png"

    if not filename.endswith('.png'):
        filename += '.png'

    filepath = path.join(save_dir, filename)
    screenshot().save(filepath)

    return path.abspath(filepath)

if __name__ == "__main__":
    while True:
        sleep(2)  # Wait before taking screenshot
        image_path = capture_screen(save_dir=SCREENSHOTS_DIR)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Screenshot taken")

        # Check if still searching for match
        searching_for_match = check_template_in_image(
            image_path,
            TEMPLATE_SEARCHING_FOR,
            confidence=0.7
        )
        if not searching_for_match:
            sleep(2)
            print("  -> In a lobby! Checking for Shoot House...")
            
            found_shoot_house = check_template_in_image(
                image_path,
                TEMPLATE_SHOOT_HOUSE,
                confidence=0.95  # High threshold to avoid false positives
            )

            if found_shoot_house:
                print("\n" + "="*70)
                print("SUCCESS! Found Shoot House lobby!")
                print("="*70)
                send_windows_notification("Found lobby with Shoot House!")
                exit(0)
            else:
                print("  -> Shoot House NOT found. Leaving lobby...")
                click_target_element(IMAGE_EXIT_QUEUE_BUTTON)
                sleep(0.2)
                click_target_element(IMAGE_YES_QUIT_GREY_BUTTON)
                sleep(0.2)
                click_target_element(IMAGE_YES_QUIT_GREEN_BUTTON)
                sleep(2)
                print("  -> Rejoining queue...")
                click_target_element(IMAGE_JOIN_QUEUE_BUTTON)
                remove(image_path)
        else:
            print("  -> Still searching for match...")
            remove(image_path)
