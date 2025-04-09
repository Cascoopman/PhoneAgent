import os
import subprocess
from datetime import datetime
from PIL import Image






def create_screenshot():
    # Ensure the screenshot directory exists
    os.makedirs(config["SCREENSHOT_DIR"], exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(config["SCREENSHOT_DIR"], f"{timestamp}.png")

    try:
        # Use shell=True carefully, ensure command is safe
        # On macOS, screencapture is a safe, standard utility
        subprocess.run(
            ["screencapture", screenshot_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Screen capture successful.")

        # Open the captured image
        with Image.open(screenshot_path) as img:
            width, height = img.size
            # Define the box for the left quarter
            # (left, upper, right, lower)
            left_quarter_box = (0, (height // 4), width // 4, height)
            # Crop the image
            cropped_img = img.crop(left_quarter_box)
            # Save the cropped image
            cropped_img.save(screenshot_path)
            print(f"Cropped left quarter saved to {screenshot_path}")

            return screenshot_path

    except subprocess.CalledProcessError as e:
        print(f"Error capturing screen: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Error: 'screencapture' command not found. Ensure you are on macOS.")
    except Exception as e:
        print(f"An error occurred during image processing: {e}")


if __name__ == "__main__":
    path = take_screenshot()
    response = gemini_query(path)
    print(response)
