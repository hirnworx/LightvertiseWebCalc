import cv2
import numpy as np
from PIL import Image, ImageDraw
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define minimum and maximum height constants
MIN_HEIGHT = 2.0  # Example minimum height in cm
MAX_HEIGHT = 250.0  # Example maximum height in cm

def process_image(filename, reference_measure_cm, ref_type):
    # Read the image
    try:
        img = cv2.imread(filename)
        if img is None:
            raise ValueError("Bild nicht gefunden oder der Pfad ist falsch")
    except Exception as e:
        logging.error(f"Fehler beim Lesen des Bildes: {e}")
        img = filename

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Threshold to create a binary image
    _, binary = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if not contours:
        raise ValueError("Keine Konturen im Bild gefunden")

    signet_contour = contours[0]
    x, y, w, h = cv2.boundingRect(signet_contour)

    # Initialize variables to hold the extreme points
    min_x, min_y, max_x, max_y = x, y, x + w, y + h
    max_height = h

    # Calculate total width and height of the entire logo
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        min_x = min(min_x, x)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    # Calculate total dimensions in pixels
    total_width_px = max_x - min_x
    total_height_px = max_y - min_y

    # Determine the scaling factor
    if ref_type == 3:  # Reference by height
        scaling_factor = reference_measure_cm / max_height
    elif ref_type == 1:  # Reference by total width
        scaling_factor = reference_measure_cm / total_width_px
    elif ref_type == 2:  # Reference by total height
        scaling_factor = reference_measure_cm / total_height_px
    else:
        raise ValueError("Ungültiger Referenztyp")

    logging.debug(f"Skalierungsfaktor: {scaling_factor}")

    # Convert to PIL Image for drawing annotations
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    output_lines = [f"Signet height: {scaling_factor * max_height:.2f} cm"]

    valid_contours = []
    invalid_heights = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        element_height_cm = scaling_factor * h
        # Filter out invalid heights
        if element_height_cm < MIN_HEIGHT or element_height_cm > MAX_HEIGHT:
            logging.debug(f"Gefilterte ungültige Höhe: {element_height_cm:.2f} cm")
            invalid_heights.append(element_height_cm)
            continue
        valid_contours.append(contour)
        draw.rectangle([x, y, x + w, y + h], outline="green", width=2)
        output_lines.append(f"Element height: {element_height_cm:.2f} cm")

    # Calculate total dimensions in cm
    total_width_cm = total_width_px * scaling_factor
    total_height_cm = total_height_px * scaling_factor

    # Add total dimensions to the output
    output_lines.append(f"Total width: {total_width_cm:.2f} cm")
    output_lines.append(f"Total height: {total_height_cm:.2f} cm")

    # Calculate positions for the total width and height annotations
    offset = 20  # Distance from the image elements to the annotations
    total_width_line_y = max_y + offset
    total_height_line_x = min_x - offset

    # Ensure the text is placed within the image boundaries
    total_width_text_y = total_width_line_y + offset if total_width_line_y + offset < img.shape[0] else total_width_line_y - offset
    total_height_text_x = total_height_line_x - offset if total_height_line_x - offset > 0 else total_height_line_x + offset

    # Draw total width and height on the image
    draw.line([(min_x, total_width_line_y), (max_x, total_width_line_y)], fill="red", width=2)
    draw.text((min_x, total_width_text_y), f"Total width: {total_width_cm:.2f} cm", fill="red")
    draw.line([(total_height_line_x, min_y), (total_height_line_x, max_y)], fill="red", width=2)
    draw.text((total_height_text_x, (min_y + max_y) // 2), f"Total height: {total_height_cm:.2f} cm", fill="red")

    # Convert back to PIL image to return it for the UI
    processed_pil_image = Image.fromarray(cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))

    return processed_pil_image, '\n'.join(output_lines), total_width_cm, total_height_cm, invalid_heights











"""
Previous Logic for reference


def process_image(filename, reference_measure_cm, ref_type):
    # Read the image
    try:
        img = cv2.imread(filename)
        file_path = "original_code_image.jpg"
        if img is None:
            raise ValueError("Image not found or the path is incorrect")
    except:
        img = filename
        file_path = "flask_server_image.jpg"

    # cv2.imwrite(file_path, img)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Threshold to create a binary image
    _, binary = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    signet_contour = contours[0]
    x, y, w, h = cv2.boundingRect(signet_contour)
    
    # Initialize variables to hold the extreme points
    min_x, min_y, max_x, max_y = x, y, x+w, y+h
    max_height = h

    # Convert to PIL Image for drawing annotations
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    # Draw the signet contour
    draw.rectangle([x, y, x + w, y + h], outline="green", width=2)

    # scaling_factor = reference_height_cm / h

    if ref_type == 3:  # Reference by height
        scaling_factor = reference_measure_cm / h
    elif ref_type == 1:  # Reference by total width
        total_width_px = max_x - min_x
        scaling_factor = reference_measure_cm / total_width_px
    elif ref_type == 2:  # Reference by total height
        total_height_px = max_y - min_y
        scaling_factor = reference_measure_cm / total_height_px
    else:
        raise ValueError("Invalid reference type")
    
    print("Scaling factor: ", scaling_factor)
    # print("max_height: ", max_height)
    output_lines = [f"Signet height: {scaling_factor * h:.2f} cm"]

    # Draw and annotate other contours
    for contour in contours[1:]:
        x, y, w, h = cv2.boundingRect(contour)
        min_x = min(min_x, x)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)
        max_height = max(max_height, h)
        element_height_cm = scaling_factor * h
        draw.rectangle([x, y, x + w, y + h], outline="green", width=2)
        output_lines.append(f"Element height: {element_height_cm:.2f} cm")

    # Calculate total width and height
    total_width_px = max_x - min_x
    total_height_px = max_y - min_y
    total_width_cm = total_width_px * scaling_factor
    total_height_cm = total_height_px * scaling_factor

    # Add total dimensions to the output
    output_lines.append(f"Total width: {total_width_cm:.2f} cm")
    output_lines.append(f"Total height: {total_height_cm:.2f} cm")

    # Calculate positions for the total width and height annotations
    offset = 20  # Distance from the image elements to the annotations
    total_width_line_y = max_y + offset
    total_height_line_x = min_x - offset

    # Ensure the text is placed within the image boundaries
    total_width_text_y = total_width_line_y + offset if total_width_line_y + offset < img.shape[0] else total_width_line_y - offset
    total_height_text_x = total_height_line_x - offset if total_height_line_x - offset > 0 else total_height_line_x + offset

    # Draw total width and height on the image
    draw.line([(min_x, total_width_line_y), (max_x, total_width_line_y)], fill="red", width=2)
    draw.text((min_x, total_width_text_y), f"Total width: {total_width_cm:.2f} cm", fill="red")
    draw.line([(total_height_line_x, min_y), (total_height_line_x, max_y)], fill="red", width=2)
    draw.text((total_height_text_x, (min_y + max_y) // 2), f"Total height: {total_height_cm:.2f} cm", fill="red")

    # Convert back to PIL image to return it for the UI
    processed_pil_image = Image.fromarray(cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR))

    return processed_pil_image, '\n'.join(output_lines)

"""