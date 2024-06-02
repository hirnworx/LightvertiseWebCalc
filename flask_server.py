from flask import Flask, request, jsonify, send_from_directory, render_template
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
import base64
import numpy as np
import cv2
import gc
import traceback
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize filename as None
filename = None

# Establish a database connection and create a table
connection = create_db_connection()
if connection is not None:
    create_table(connection)

def start_database_monitor():
    script_path = os.path.join(os.path.dirname(__file__), 'database_monitor.py')
    subprocess.Popen([os.getcwd(), script_path], shell=True)

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

# def process_image_thread(filename, reference_height, customer_data):
def process_image_thread(image, reference_height, customer_data):
    # if filename is None:
    #     messagebox.showerror("File Not Found", "Filename is not defined. Make sure a file is selected.")
    #     return

    try:
        calculation_data = rail_price = error = None

        processed_pil_image, output_string = image_processor.process_image(image, reference_height)

        # Apply Gaussian Blur
        processed_pil_image = processed_pil_image.filter(ImageFilter.GaussianBlur(radius=0.0))

        # cv2.imwrite("processed_pil_image.jpg", cv2.cvtColor(np.array(processed_pil_image), cv2.COLOR_RGB2BGR))
        _ , img_jpg = cv2.imencode('.jpg', cv2.cvtColor(np.array(processed_pil_image), cv2.COLOR_RGB2BGR))
        image_data = str(base64.b64encode(img_jpg))

        # tk_image = ImageTk.PhotoImage(image=processed_pil_image)
        # output_text.after(0, lambda: output_text.insert(END, output_string))
        # image_label.after(0, lambda: update_image_label(tk_image))

        heights = [float(line.split()[2]) for line in output_string.split('\n') if 'Element height' in line]
        total_price = sum(profile5s(height) for height in heights)

        total_width_cm_line = [line for line in output_string.split('\n') if 'Total width' in line][0]
        total_width_cm = float(total_width_cm_line.split()[2])
        rail_price = calculate_railprice(total_width_cm)
        
        price_including_rail = total_price + rail_price

        # buffered = io.BytesIO()
        # processed_pil_image.save(buffered, format="JPEG")
        # image_data = buffered.getvalue()
        
        # output_text.after(0, lambda: output_text.insert(END, f"\nTotal Price: {total_price}€"))
        # output_text.after(0, lambda: output_text.insert(END, f"\nRail Price: {rail_price}€"))
        # output_text.after(0, lambda: output_text.insert(END, f"\nPrice including Rail: {price_including_rail}€\n"))

        # if connection is not None:
        calculation_data = {
            "calculation_data": output_string.split('\n'),
            "price_without_rail": total_price,
            "price_with_rail": price_including_rail,
            "reference_height": reference_height,
            "output_image": image_data
        }
            # insert_calculation_result(connection, calculation_data, customer_data)  # Pass customer_data here

        return calculation_data, customer_data, rail_price, error

    except Exception as ex:
        # messagebox.showerror("Processing Error", str(e))

        error = traceback.format_exc()
        print("\n")
        print("------------------------------------------------")
        print("   ERROR:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Error traceback ---------------")
        print(error)
        print("------------------------------------------------")
        print("\n")

        return calculation_data, customer_data, rail_price, error




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



@app.route('/calculate_logo_data',methods=['POST'])
def calculate_logo_data():

    try:
        results = {}

        if len(request.form) > 0:
            data = json.loads(request.form['data'])
        else:
            data = request.json

        print(data)

        image = request.json['image_data']
        image_type = request.json['image_type']
        reference_height = float(request.json['reference_height'])
        
        customer_data = {
            "customer_name": request.json['customer_name'],
            "customer_street": request.json['customer_street'],
            "customer_city": request.json['customer_city'],
            "customer_zipcode": request.json['customer_zipcode'],
            "customer_phone": request.json['customer_phone'],
            "customer_email": request.json['customer_email']
        }

        # customer_data = {
        #     "customer_name": '',
        #     "customer_street": '',
        #     "customer_city": '',
        #     "customer_zipcode": '',
        #     "customer_phone": '',
        #     "customer_email": ''
        # }

        # jpg_original = base64.b64decode(image)
        # jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        # image = cv2.imdecode(jpg_as_np, flags=1)

        # image = Image.fromarray(np.uint8(image)).convert('RGB')

        base64_decoded = base64.b64decode(image)
        image = Image.open(io.BytesIO(base64_decoded))
 
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
            background.paste(image, image.split()[-1])  # Exclude the alpha channel
            image = background
        image = image.convert('RGB')
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        calculation_data, customer_data, rail_price, error = process_image_thread(image, reference_height, customer_data)

        # print(customer_data)

        if error == None:

            results['element_heights'] = []

            for element_data in calculation_data['calculation_data']:
                element_data = element_data.split(':')
                # print(element_data, 'Element height' in element_data[0], 'Signet height' in element_data[0])
                if 'Element height' in element_data[0]:
                    results['element_heights'].append(element_data[1].strip())
                elif 'Signet height' in element_data[0]:
                    results['signet_height'] = element_data[1].strip()
                elif 'Total width' in element_data[0]:
                    results['total_width'] = element_data[1].strip()
                elif 'Total height' in element_data[0]:
                    results['total_height'] = element_data[1].strip()

            results['total_price'] = calculation_data['price_without_rail']
            results['price_including_rail'] = calculation_data['price_with_rail']
            results['rail_price'] = rail_price
            # results['reference_height'] = calculation_data['reference_height']
            results['output_image'] = calculation_data['output_image']
            results['customer_data'] = customer_data

            print("results: ", results)
            
            message = {
                # 'status': 200,
                'error': None,
                'data': results
            }
            resp = jsonify(message)
            resp.status_code = 200

            del data, results, message
            gc.collect()
            return resp

        else:
            message = {
                # 'status': 500,
                'error': error,
                'data': results
            }
            resp = jsonify(message)
            resp.status_code = 500
            return resp

    except Exception as ex:
        # activeStream.remove(videoId)
        # print("After, Active Stream: ", activeStream)
        print("\n")
        print("------------------------------------------------")
        print("   ERROR:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Error traceback ---------------")
        print(traceback.format_exc())
        print("------------------------------------------------")
        print("\n")

        message = {
            # 'status': 500,
            'error': str(traceback.format_exc()),
            'data': results
        }
        resp = jsonify(message)
        resp.status_code = 500
        return resp



    
@app.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/', methods=["GET","POST"])
def html():
    return render_template('index.html')

# root = tk.Tk()
# root.title('Letter Size Identifier')

# # Use style to improve the appearance
# style = ttk.Style(root)
# style.theme_use('clam')  # You can experiment with different themes

# # Define frames for better organization
# frame_top = ttk.Frame(root, padding="10")
# frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# frame_bottom = ttk.Frame(root, padding="10")
# frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# # Use ttk widgets for a better appearance
# upload_btn = ttk.Button(frame_top, text='Upload Image', command=upload_action)
# upload_btn.pack()

# filename_label = ttk.Label(frame_top, text='No file selected')
# filename_label.pack()

# height_label = ttk.Label(frame_top, text='Enter the tallest letter height in cm:')
# height_label.pack()

# height_entry = ttk.Entry(frame_top)
# height_entry.pack()

# # Customer Data Labels and Entry Fields
# customer_name_label = Label(root, text='Customer Name:')
# customer_name_label.pack()

# customer_name_entry = Entry(root)
# customer_name_entry.pack()

# customer_street_label = Label(root, text='Street:')
# customer_street_label.pack()

# customer_street_entry = Entry(root)
# customer_street_entry.pack()

# customer_city_label = Label(root, text='City:')
# customer_city_label.pack()

# customer_city_entry = Entry(root)
# customer_city_entry.pack()

# customer_zipcode_label = Label(root, text='Zip Code:')
# customer_zipcode_label.pack()

# customer_zipcode_entry = Entry(root)
# customer_zipcode_entry.pack()

# customer_phone_label = Label(root, text='Phone Number:')
# customer_phone_label.pack()

# customer_phone_entry = Entry(root)
# customer_phone_entry.pack()

# customer_email_label = Label(root, text='Email Address:')
# customer_email_label.pack()

# customer_email_entry = Entry(root)
# customer_email_entry.pack()

# height_btn = ttk.Button(frame_top, text='Set Height', command=define_reference_height)
# height_btn.pack()

# reset_btn = ttk.Button(frame_top, text='Reset', command=reset_fields)
# reset_btn.pack()

# output_text = Text(frame_bottom, height=10, width=50)
# output_text.pack()

# scrollbar = ttk.Scrollbar(frame_bottom, command=output_text.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# output_text.config(yscrollcommand=scrollbar.set)

# image_label = ttk.Label(frame_bottom)
# image_label.pack()

# start_database_monitor()
# root.mainloop()

# if connection is not None:
#     close_connection(connection)

# return

    

################################### END ##################################################
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
