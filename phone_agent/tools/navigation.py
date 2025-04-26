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


def home_screen(explanation: str) -> dict:
    """
    Go back to the home screen of the iPhone.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.

    Returns:
        dict: The outcome of clicking the home button.
    """
    x = config["HOME_BUTTON_X"]
    y = config["HOME_BUTTON_Y"]
    y = config["SCREEN_Y_INVERSION"] - y

    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # Let the UI update
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "home button clicked"}


def move_pointer(explanation: str, x: int, y: int) -> dict:
    """
    Move the pointer to the specified coordinates.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        x (int): The x coordinate to move to.
        y (int): The y coordinate to move to.

    Returns:
        dict: The outcome of the move pointer process.
    """
    if x > config["SCREEN_X_BOUND"] or x < 0:
        return {
            "status": "error",
            "message": f"""Invalid coordinates.
            The x values should be between 0 and {config["SCREEN_X_BOUND"]}.
            """,
        }
    if y > config["SCREEN_Y_BOUND"] or y < 0:
        return {
            "status": "error",
            "message": f"""Invalid coordinates.
            The y values should be between 0 and {config["SCREEN_Y_BOUND"]}.
            """,
        }

    y = config["SCREEN_Y_INVERSION"] - y

    pyautogui.moveTo(x, y)
    time.sleep(0.1)  # Let the UI update
    return {"status": "pointer moved"}


def click_pointer(explanation: str) -> dict:
    """
    Click on the screen at the current pointer position.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.

    Returns:
        dict: The outcome of the click process.
    """
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    return {"status": "pointer clicked"}


def _drag_screen(x_offset: int, y_offset: int) -> dict:
    y_offset = -y_offset
    pyautogui.drag(x_offset, y_offset, duration=0.15, button="left")
    time.sleep(0.1)
    return {"status": "scrolled screen"}


def _scroll_left() -> dict:
    return _drag_screen(100, 0)


def _scroll_right() -> dict:
    return _drag_screen(-100, 0)


def _scroll_up() -> dict:
    return _drag_screen(0, 100)


def _scroll_down() -> dict:
    return _drag_screen(0, -100)


def scroll_screen(explanation: str, direction: str) -> dict:
    """
    Scroll across the screen in the specified direction.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        direction (str): The direction to swipe. The direction must be "left", "right", "up", or "down".

    Returns:
        dict: The outcome of the swipe process.
    """
    if direction == "left":
        return _scroll_left()
    elif direction == "right":
        return _scroll_right()
    elif direction == "up":
        return _scroll_up()
    elif direction == "down":
        return _scroll_down()


def enter_keys(explanation: str, keys: str) -> dict:
    """Enter keys in the current selected text field.
    Requires a text field to be selected first.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        keys (str): The keys to enter in the text field.

    Returns:
        dict: The outcome of the key entry process.
    """
    try:
        for key in keys:
            pyautogui.press(key)
            time.sleep(0.1)
    except Exception as e:
        return {"status": "error", "message": f"Error entering keys: {str(e)}"}
    return {"status": "keys entered"}


if __name__ == "__main__":
    print(move_pointer(explanation="", x=277, y=599))
    print(click_pointer(explanation=""))
