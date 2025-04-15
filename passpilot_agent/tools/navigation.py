import os
import time

import pyautogui
from dotenv import load_dotenv

load_dotenv()

config = {
    "SCREENSHOT_DIR": os.getenv("SCREENSHOT_DIR"),
    "SCREEN_Y_BOUND": int(os.getenv("MIRRORING_Y_BOUND")),
    "SCREEN_X_BOUND": int(os.getenv("MIRRORING_X_BOUND")),
    "SCREEN_Y_INVERSION": int(os.getenv("SCREEN_Y_INVERSION")),
    "HOME_BUTTON_X": int(os.getenv("HOME_BUTTON_X")),
    "HOME_BUTTON_Y": int(os.getenv("HOME_BUTTON_Y")),
}


def home_screen():
    """
    This tool is used to go back to the iPhone home screen.
    """
    x = config["HOME_BUTTON_X"]
    y = config["HOME_BUTTON_Y"]
    y = config["SCREEN_Y_INVERSION"] - y

    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # Let the UI update
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "ok"}


def move_pointer_to_position(x: int, y: int) -> dict:
    """
    This tool is used to move the pointer to the exact coordinates.
    The coordinates are percentages of the screen size.
    X is horizontal and Y is vertical.
    X=0 is left edge of the screen and X=100 is the right edge.
    Y=0 is the bottom edge of the screen and Y=100 is the top edge.

    Args:
        x (int): The x coordinate to move to, in percentage of the screen width.
        y (int): The y coordinate to move to, in percentage of the screen heights.
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


def move_pointer_from_current_to(x: int, y: int) -> dict:
    """
    This tool is used to move the pointer relative from the current position.

    Args:
        x (int): The x distance to move, in absolute percentage of the screen width.
        y (int): The y distance to move, in absolute percentage of the screen heights.
    """
    current_x, current_y = pyautogui.position()

    x = config["SCREEN_X_BOUND"] * (x / 100)
    y = config["SCREEN_Y_BOUND"] * (y / 100)
    y = config["SCREEN_Y_INVERSION"] - y

    new_x = current_x + x
    new_y = current_y + y

    if new_x > config["SCREEN_X_BOUND"] or new_x < 0:
        return {
            "status": "error",
            "message": "Invalid x coordinate. The values should be between 0 and 100.",
        }
    if new_y > config["SCREEN_Y_BOUND"] or new_y < 0:
        return {
            "status": "error",
            "message": "Invalid y coordinate. The values should be between 0 and 100.",
        }

    pyautogui.moveTo(new_x, new_y)
    time.sleep(0.1)
    return {"status": "ok"}


def click_pointer() -> dict:
    """
    This tool is used to click on the iPhone screen at the current pointer position.
    """
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "ok"}


def _swipe_screen(x_offset: int, y_offset: int) -> dict:
    """
    Performs a mouse drag relative from its current position.

    Args:
        x_offset (int): The x offset to drag to.
        y_offset (int): The y offset to drag to.
    """
    y_offset = -y_offset
    pyautogui.drag(x_offset, y_offset, duration=0.15, button="left")
    time.sleep(0.1)
    return {"status": "ok"}


def swipe_left() -> dict:
    """
    This tool is used to swipe left on the iPhone screen.
    """
    return _swipe_screen(-100, 0)


def swipe_right() -> dict:
    """
    This tool is used to swipe right on the iPhone screen.
    """
    return _swipe_screen(100, 0)


def swipe_up() -> dict:
    """
    This tool is used to swipe up on the iPhone screen.
    """
    return _swipe_screen(0, -100)


def swipe_down() -> dict:
    """
    This tool is used to swipe down on the iPhone screen.
    """
    return _swipe_screen(0, 100)


def swipe_screen(direction: str) -> dict:
    """
    This tool is used to swipe on the iPhone screen.

    Args:
        direction (str): The direction to swipe.

    Returns:
        dict: The outcome of the swipe, either "ok" or "error".
    """
    if direction == "left":
        return swipe_left()
    elif direction == "right":
        return swipe_right()
    elif direction == "up":
        return swipe_up()
    elif direction == "down":
        return swipe_down()


def enter_keys(keys: str) -> dict:
    """
    This tool is used to enter keys on the iPhone screen.
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
    move_pointer_to_position,
    move_pointer_from_current_to,
    click_pointer,
    swipe_screen,
    enter_keys,
]
