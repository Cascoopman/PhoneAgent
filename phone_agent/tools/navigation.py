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
    Navigates the iPhone back to the home screen. Equivalent to the primary home
    gesture (swipe up from bottom or home button press). Use this to establish a
    known starting state.

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
    Moves the touch pointer to a specific coordinate (x, y) on the screen.
    Coordinates must be obtained first using the `locate_UI_elements` tool.
    After locating the element, use this tool to move the pointer to the element.
    Do not guess coordinates.
    Always verify the result using the `take_screenshot` tool.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        x (int): The target x-coordinate for the pointer.
        y (int): The target y-coordinate for the pointer.

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
    Performs a click action at the current touch pointer location. Ensure the
    pointer is correctly positioned using `move_pointer` before calling this.
    This tool does not accept any coordinates as input.
    Always verify the result using the `take_screenshot` tool.

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


def _center_mouse() -> dict:
    x_center, y_center = config["SCREEN_X_BOUND"] / 2, config["SCREEN_Y_BOUND"] / 2
    move_pointer(explanation="", x=x_center, y=y_center)
    time.sleep(0.1)
    return {"status": "mouse centered"}


def _hscroll_screen(direction: int) -> dict:
    _center_mouse()

    clicks = 5000 if direction == 1 else -5000
    pyautogui.hscroll(clicks=clicks)
    pyautogui.hscroll(clicks=clicks)
    time.sleep(0.1)
    return {"status": "scrolled screen"}


def _vscroll_screen(direction: int) -> dict:
    _center_mouse()

    clicks = 5000 if direction == 1 else -5000
    pyautogui.vscroll(clicks=clicks)
    pyautogui.vscroll(clicks=clicks)
    time.sleep(0.1)
    return {"status": "scrolled screen"}


def _scroll_left() -> dict:
    return _hscroll_screen(1)


def _scroll_right() -> dict:
    return _hscroll_screen(-1)


def _scroll_up() -> dict:
    return _vscroll_screen(1)


def _scroll_down() -> dict:
    return _vscroll_screen(-1)


def scroll_screen(explanation: str, direction: str) -> dict:
    """
    Scrolls the screen content in a specified direction (up, down, left, right).
    Use this to reveal elements that are currently off-screen.
    Always verify the result using the `take_screenshot` tool.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        direction (str): The direction to swipe. The direction must be "left", "right", "up", or "down".

    Returns:
        dict: The outcome of the swipe process.
    """
    direction = direction.lower().strip()
    if direction == "left":
        return _scroll_left()
    elif direction == "right":
        return _scroll_right()
    elif direction == "up":
        return _scroll_up()
    elif direction == "down":
        return _scroll_down()
    else:
        return {"status": "error", "message": "Invalid direction"}


def enter_keys(explanation: str, text: str) -> dict:
    """
    Enters the specified text into the currently focused text input field.
    This tool is only able to enter default characters found on a physical QWERTY keyboard.
    It does not support special characters or emojis.
    Ensure a text field is selected before calling this. For sensitive
    information like passwords, confirm with the USER first if not explicitly
    permitted.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        text (str): The text sequence to enter.

    Returns:
        dict: The outcome of the key entry process.
    """
    try:
        for key in text:
            pyautogui.press(key)
            time.sleep(0.1)
    except Exception as e:
        return {"status": "error", "message": f"Error entering keys: {str(e)}"}
    return {"status": "keys entered"}


if __name__ == "__main__":
    print(move_pointer(explanation="", x=150, y=330))
    print(scroll_screen(explanation="", direction="up"))
