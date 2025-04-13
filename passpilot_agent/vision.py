import cv2
import os # Import os for path manipulation

def detect_buttons(image_path):
    """
    Loads an image, detects potential button-like rectangular contours,
    draws bounding boxes and center coordinates, and saves the result.

    Args:
        image_path (str): Path to the screenshot image file.

    Returns:
        str: The path to the saved output image, or None if an error occurred.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    # Use RETR_EXTERNAL to get only outer contours
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Found {len(contours)} initial contours.")

    potential_buttons = []
    min_area = 500  # Adjust min area threshold as needed
    max_area = 50000 # Adjust max area threshold as needed

    for contour in contours:
        # Approximate the contour to a polygon
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * peri, True) # Adjust epsilon (0.03)

        # Filter based on area and number of vertices (e.g., 4 for rectangles)
        area = cv2.contourArea(contour)
        # print(f"Contour area: {area}, Vertices: {len(approx)}") # Debug print

        # Basic filtering: check if it's somewhat rectangular and within area bounds
        if len(approx) >= 4 and len(approx) <= 6 and min_area < area < max_area:
             # Get bounding box
            x, y, w, h = cv2.boundingRect(approx)

            # Filter based on aspect ratio (optional, adjust as needed)
            aspect_ratio = float(w)/h
            # print(f"Aspect ratio: {aspect_ratio}") # Debug print
            # Example: filter for typical button aspect ratios (wider than tall)
            # if 0.5 < aspect_ratio < 5.0:
            potential_buttons.append((x, y, w, h))
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2) # Draw green box
            
            # Add text with coordinates
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_color = (0, 0, 255) # Red color
            thickness = 1
            # Calculate center coordinates
            center_x = x + w // 2
            center_y = y + h // 2
            text = f"({center_x},{center_y})" # Display center coords
            # Position text slightly above the top-left corner
            text_position = (x, y - 10 if y > 20 else y + h + 15) # Adjust position if too close to top
            cv2.putText(img, text, text_position, font, font_scale, font_color, thickness, cv2.LINE_AA)
    print(f"Found {len(potential_buttons)} potential button regions.")

    # Save the result instead of displaying
    try:
        success = cv2.imwrite(image_path, img)
        if success:
            print(f"Output image saved to: {image_path}")
            return image_path
        else:
            print(f"Error: Could not save image to {image_path}")
            return None
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

if __name__ == "__main__":
    # Define input and output paths
    input_screenshot = '/Users/caswork/Projects/chapter-work/PassPilot/screenshots/20250413_223955.png'

    if not os.path.exists(input_screenshot):
        print(f"Error: Input file not found at {input_screenshot}")
    else:
        saved_image_path = detect_buttons(input_screenshot)
        if not saved_image_path:
            print("Script finished with errors.")

# Note: You'll need OpenCV installed: pip install opencv-python numpy
# This is a very basic detector and results will vary greatly. Adjust thresholds (min_area, max_area, epsilon in approxPolyDP, aspect_ratio) for your specific UI.
