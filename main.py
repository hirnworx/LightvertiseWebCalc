import tkinter as tk
from tkinter import ttk, filedialog, Label, Entry, Text, messagebox
from PIL import Image, ImageTk, ImageFilter
from pdf2image import convert_from_path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from tkinter import END
import threading
import subprocess
import image_processor
import os
import io
from pricing import profile5s, calculate_railprice
from database.db_operations import create_db_connection, create_table, insert_calculation_result, close_connection

# Initialize filename as None
filename = None

# Establish a database connection and create a table
connection = create_db_connection()
if connection is not None:
    create_table(connection)

def start_database_monitor():
    script_path = os.path.join(os.path.dirname(__file__), 'database_monitor.py')
    subprocess.Popen([os.getcwd(), script_path], shell=True)

if __name__ == '__main__':
    start_database_monitor()

def upload_action(event=None):
    global filename
    filename = filedialog.askopenfilename()
    filename_label.config(text=f"Selected File: {filename}")
    output_text.delete('1.0', END)
    image_label.config(image=None)

    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.svg')):
        if filename.lower().endswith('.svg'):
            drawing = svg2rlg(filename)
            png_filename = f"{os.path.splitext(filename)[0]}.png"
            renderPM.drawToFile(drawing, png_filename, fmt="PNG", configPIL={'backend': 'PIL'})
            filename = png_filename

        image = Image.open(filename)
        print(image.mode)
        print(image.info)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
            background.paste(image, image.split()[-1])  # Exclude the alpha channel
            image = background
        image = image.convert('RGB')
        filename = f"{os.path.splitext(filename)[0]}_converted.jpg"
        image.save(filename)
    elif filename.lower().endswith('.pdf'):
        images = convert_from_path(filename)
        if images:
            image = images[0]
            image = image.convert('RGB')
            filename = f"{os.path.splitext(filename)[0]}_page1.jpg"
            image.save(filename)
    else:
        messagebox.showerror("Unsupported File", "The selected file format is not supported.")

def define_reference_height(event=None):
    try:
        reference_height = float(height_entry.get())
        customer_data = {
            "customer_name": customer_name_entry.get(),
            "customer_street": customer_street_entry.get(),
            "customer_city": customer_city_entry.get(),
            "customer_zipcode": customer_zipcode_entry.get(),
            "customer_phone": customer_phone_entry.get(),
            "customer_email": customer_email_entry.get()
        }
        threading.Thread(target=process_image_thread, args=(filename, reference_height, customer_data), daemon=True).start()
    except ValueError:
        messagebox.showerror("Invalid Input", "Invalid height value. Please enter a valid number.")

def process_image_thread(filename, reference_height, customer_data):
    if filename is None:
        messagebox.showerror("File Not Found", "Filename is not defined. Make sure a file is selected.")
        return

    try:
        processed_pil_image, output_string = image_processor.process_image(filename, reference_height)

        # print("output_string: ", output_string)

        # Apply Gaussian Blur
        processed_pil_image = processed_pil_image.filter(ImageFilter.GaussianBlur(radius=0.0))

        tk_image = ImageTk.PhotoImage(image=processed_pil_image)
        output_text.after(0, lambda: output_text.insert(END, output_string))
        image_label.after(0, lambda: update_image_label(tk_image))

        heights = [float(line.split()[2]) for line in output_string.split('\n') if 'Element height' in line]
        total_price = sum(profile5s(height) for height in heights)

        total_width_cm_line = [line for line in output_string.split('\n') if 'Total width' in line][0]
        total_width_cm = float(total_width_cm_line.split()[2])
        rail_price = calculate_railprice(total_width_cm)
        
        price_including_rail = total_price + rail_price

        buffered = io.BytesIO()
        processed_pil_image.save(buffered, format="JPEG")
        image_data = buffered.getvalue()
        
        output_text.after(0, lambda: output_text.insert(END, f"\nTotal Price: {total_price}€"))
        output_text.after(0, lambda: output_text.insert(END, f"\nRail Price: {rail_price}€"))
        output_text.after(0, lambda: output_text.insert(END, f"\nPrice including Rail: {price_including_rail}€\n"))

        if connection is not None:
            calculation_data = {
                "calculation_data": output_string.split('\n'),
                "price_without_rail": total_price,
                "price_with_rail": price_including_rail,
                "reference_height": reference_height,
                "output_image": image_data
            }
            insert_calculation_result(connection, calculation_data, customer_data)  # Pass customer_data here

            # print(calculation_data)
            # print(customer_data)

    except Exception as e:
        messagebox.showerror("Processing Error", str(e))



def update_image_label(tk_image):
    image_label.config(image=tk_image)
    image_label.image = tk_image
    max_width = 300

def reset_fields(event=None):
    global filename
    filename_label.config(text="No file selected")
    height_entry.delete(0, tk.END)
    output_text.delete('1.0', END)
    image_label.config(image=None)

root = tk.Tk()
root.title('Letter Size Identifier')

# Use style to improve the appearance
style = ttk.Style(root)
style.theme_use('clam')  # You can experiment with different themes

# Define frames for better organization
frame_top = ttk.Frame(root, padding="10")
frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

frame_bottom = ttk.Frame(root, padding="10")
frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Use ttk widgets for a better appearance
upload_btn = ttk.Button(frame_top, text='Upload Image', command=upload_action)
upload_btn.pack()

filename_label = ttk.Label(frame_top, text='No file selected')
filename_label.pack()

height_label = ttk.Label(frame_top, text='Enter the tallest letter height in cm:')
height_label.pack()

height_entry = ttk.Entry(frame_top)
height_entry.pack()

# Customer Data Labels and Entry Fields
customer_name_label = Label(root, text='Customer Name:')
customer_name_label.pack()

customer_name_entry = Entry(root)
customer_name_entry.pack()

customer_street_label = Label(root, text='Street:')
customer_street_label.pack()

customer_street_entry = Entry(root)
customer_street_entry.pack()

customer_city_label = Label(root, text='City:')
customer_city_label.pack()

customer_city_entry = Entry(root)
customer_city_entry.pack()

customer_zipcode_label = Label(root, text='Zip Code:')
customer_zipcode_label.pack()

customer_zipcode_entry = Entry(root)
customer_zipcode_entry.pack()

customer_phone_label = Label(root, text='Phone Number:')
customer_phone_label.pack()

customer_phone_entry = Entry(root)
customer_phone_entry.pack()

customer_email_label = Label(root, text='Email Address:')
customer_email_label.pack()

customer_email_entry = Entry(root)
customer_email_entry.pack()

height_btn = ttk.Button(frame_top, text='Set Height', command=define_reference_height)
height_btn.pack()

reset_btn = ttk.Button(frame_top, text='Reset', command=reset_fields)
reset_btn.pack()

output_text = Text(frame_bottom, height=10, width=50)
output_text.pack()

scrollbar = ttk.Scrollbar(frame_bottom, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

image_label = ttk.Label(frame_bottom)
image_label.pack()

root.mainloop()

if connection is not None:
    close_connection(connection)
