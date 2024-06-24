# validator.py

from pricing import MIN_HEIGHT, MAX_HEIGHT

def validate_heights(heights):
    invalid_heights = [height for height in heights if height < MIN_HEIGHT or height > MAX_HEIGHT]
    suggestions = {
        'min_height': MIN_HEIGHT,
        'max_height': MAX_HEIGHT
    }
    return invalid_heights, suggestions

def validate_dimensions(total_width):
    min_width = MIN_HEIGHT * 5  # Example logic, adjust as necessary
    max_width = MAX_HEIGHT * 10  # Example logic, adjust as necessary
    suggestions = {
        'min_width': min_width,
        'max_width': max_width
    }
    return total_width >= min_width and total_width <= max_width, suggestions
