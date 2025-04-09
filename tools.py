
from google.genai import types

import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def click_screen(x: int, y: int):
    if y > config["SCREEN_Y_BOUND"] or x > config["SCREEN_X_BOUND"]:
        return "Invalid coordinates. Please provide coordinates within the screen bounds."
    
    y = config["SCREEN_Y_BOUND"] - y
    import pyautogui
    pyautogui.click(x, y)
    return f"Clicked on the screen at x: {x}, y: {y} successfully."


def swipe_screen(x: int, y: int, direction: str, distance: int):
    import pyautogui
    pyautogui.moveTo(x, y)
    pyautogui.drag(x_distance, y_distance, duration=0.5)
    return f"Swiped on the screen at x: {x}, y: {y} in the {direction} direction for {distance} pixels successfully."


def home_screen():
    subprocess.run(["touch", "/tmp/home.txt"], check=True, capture_output=True, text=True)
    return "Home screen opened successfully."

def take_screenshot():
    agent.get_history().append(
    types.Content(
        parts=[
            types.Image(
                file_uri=take_screenshot(),
                mime_type="image/png",
            )
        ]
    )
)

if __name__ == "__main__":
    click_screen(200, 500)
