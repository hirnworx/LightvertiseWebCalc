# pricing.py

def profile5s(typeheight_cm, upcharge_percent=80):
    # Convert centimeters to millimeters for comparison
    typeheight_mm = int(typeheight_cm * 10)
    
    # Define the explicit price points based on height in mm

    # price_points = {
    #     100: 139,
    #     251: 169,
    #     301: 188,
    #     401: 215,
    #     501: 250,
    #     601: 290,
    #     701: 340,
    #     801: 400,
    #     901: 459,
    #     1001: 459  # Assuming the price does not increase after 1000 mm
    # }

    price_points = {
        100: 139,
        125: 139,
        150: 139,
        200: 139,
        250: 139,
        300: 169,
        350: 188,
        400: 188,
        450: 215,
        500: 215,
        600: 250,
        700: 290,
        800: 340,
        900: 400,
        1000: 459,
        1100: 500,
        1200: 540,
        1300: 580,
        1400: 620,
        1500: 660.,
        1600: 700,
        1700: 740,
        1800: 780,
        1900: 820,
        2000: 860,
        2100: 900,
        2200: 940,
        2300: 980,
        2400: 1020,
        2501: 1060}

    # Find the two closest explicit price points
    lower_bound = max([point for point in price_points.keys() if point <= typeheight_mm])
    upper_bound = min([point for point in price_points.keys() if point > typeheight_mm])
    
    # Linear interpolation for intermediate values
    if lower_bound != upper_bound:
        price_per_mm = (price_points[upper_bound] - price_points[lower_bound]) / (upper_bound - lower_bound)
        price = price_points[lower_bound] + (typeheight_mm - lower_bound) * price_per_mm
    else:
        price = price_points[lower_bound]
    
    # Apply upcharge in percent
    total_price = price * (1 + upcharge_percent / 100)
    
    # Round the total price to 2 decimal places
    total_price = round(total_price, 2)
    
    return total_price

def calculate_railprice(total_width_cm):
    rail_price = total_width_cm * 1.9
    return round(rail_price, 2)  # Round to 2 decimal places for consistency

# Example usage:
height_in_cm = 69  # Example height in cm
upcharge_percent = 10  # Example upcharge percent
price = profile5s(height_in_cm, upcharge_percent)
print(f"The price for {height_in_cm} cm with {upcharge_percent}% upcharge is {price} Euros.")

MIN_HEIGHT = 20.0  # Example minimum height in cm
MAX_HEIGHT = 250.0  # Example maximum height in cm
