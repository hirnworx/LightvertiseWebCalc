from price_points_letters import price_points_all_letters
MIN_HEIGHT = 20.0  # Example minimum height in cm
MAX_HEIGHT = 250.0  # Example maximum height in cm

def letter_price_calculator(typeheight_cm, letter_type, upcharge_percent=80):
    # Convert centimeters to millimeters for comparison
    typeheight_mm = int(typeheight_cm * 10)
    
    
    # Price points for height in mm as per letter type
    price_points = price_points_all_letters[letter_type]
    # print(letter_type, price_points)

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

if __name__ == '__main__':

    # Example usage:
    height_in_cm = 69  # Example height in cm
    letter_type = 'halo'
    upcharge_percent = 10  # Example upcharge percent
    price = letter_price_calculator(height_in_cm, letter_type, upcharge_percent)
    print(f"The price for {height_in_cm} cm with {upcharge_percent}% upcharge is {price} Euros.")
