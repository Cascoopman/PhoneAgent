import os
import time

import pyautogui
from dotenv import load_dotenv

load_dotenv()

config = {
    "SCREEN_Y_BOUND": int(os.getenv("MIRRORING_Y_BOUND")),
    "SCREEN_X_BOUND": int(os.getenv("MIRRORING_X_BOUND")),
    "SCREEN_Y_INVERSION": int(os.getenv("SCREEN_Y_INVERSION")),
    "HOME_BUTTON_X": int(os.getenv("HOME_BUTTON_X")),
    "HOME_BUTTON_Y": int(os.getenv("HOME_BUTTON_Y")),
}


def home_screen():
    """Go back to the home screen of the device.
    The home screen contains the app icons.

    Returns:
        dict: The outcome of the home screen, either "ok" or "error".
    """
    x = config["HOME_BUTTON_X"]
    y = config["HOME_BUTTON_Y"]
    y = config["SCREEN_Y_INVERSION"] - y

    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # Let the UI update
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "ok"}


def move_pointer(x: int, y: int) -> dict:
    """Move the pointer to the specified coordinates.
    Important:
        X ranges from 0 (left) to 100 (right).
        Y ranges from 0 (bottom) to 100 (top).

    Args:
        x (int): The x coordinate to move to.
        y (int): The y coordinate to move to.

    Returns:
        dict: The outcome of the move, either "ok" or "error".
    """
    if x > 100 or y > 100 or x < 0 or y < 0:
        return {
            "status": "error",
            "message": "Invalid coordinates. The values should be between 0 and 100.",
        }

    x = config["SCREEN_X_BOUND"] * (x / 100)
    y = config["SCREEN_Y_BOUND"] * (y / 100)
    y = config["SCREEN_Y_INVERSION"] - y

    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # Let the UI update
    return {"status": "ok"}


def click_pointer() -> dict:
    """Click on the screen at the current pointer position.
    Important:
        The pointer must be moved to the desired position first.

    Returns:
        dict: The outcome of the click, either "ok" or "error".
    """
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "ok"}


def _drag_screen(x_offset: int, y_offset: int) -> dict:
    y_offset = -y_offset
    pyautogui.drag(x_offset, y_offset, duration=0.15, button="left")
    time.sleep(0.1)
    return {"status": "ok"}


def _scroll_left() -> dict:
    return _drag_screen(100, 0)


def _scroll_right() -> dict:
    return _drag_screen(-100, 0)


def _scroll_up() -> dict:
    return _drag_screen(0, 100)


def _scroll_down() -> dict:
    return _drag_screen(0, -100)


def scroll_screen(direction: str) -> dict:
    """Scroll across the screen in the specified direction.
    Important: scrolling down will move the screen up and vice versa.

    Args:
        direction (str): The direction to swipe.
        The direction can be "left", "right", "up", or "down".

    Returns:
        dict: The outcome of the swipe, either "ok" or "error".
    """
    if direction == "left":
        return _scroll_left()
    elif direction == "right":
        return _scroll_right()
    elif direction == "up":
        return _scroll_up()
    elif direction == "down":
        return _scroll_down()


def enter_keys(keys: str) -> dict:
    """Enter keys in the current selected text field.
    Requires a text field to be selected first.

    Args:
        keys (str): The keys to enter in the text field.

    Returns:
        dict: The outcome of the key entry, either "ok" or "error".
    """
    try:
        for key in keys:
            pyautogui.press(key)
            time.sleep(0.1)
    except Exception as e:
        return {"status": "error", "message": f"Error entering keys: {str(e)}"}
    return {"status": "ok"}


navigation_tools = [
    home_screen,
    move_pointer,
    click_pointer,
    scroll_screen,
    enter_keys,
]
