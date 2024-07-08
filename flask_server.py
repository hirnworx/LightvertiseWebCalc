from flask import Flask, request, jsonify, send_from_directory, render_template
import threading
import subprocess
import os
import io
import base64
import gc
import traceback
from PIL import Image, ImageFilter
import numpy as np
import cv2
import image_processor
import vector_to_jpeg
from pricing import profile5s, calculate_railprice
from database.db_operations import create_db_connection, create_table, insert_calculation_result
from validator import validate_heights, validate_dimensions
from flask_cors import CORS
from send_email import send_email  # Import the send_email function

app = Flask(__name__)
CORS(app)

# Set SendGrid API Key directly
os.environ['SENDGRID_API_KEY'] = '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'

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

    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image = Image.open(filename)
        if image.width < 350:
            messagebox.showerror("Bitte laden Sie ein größeres Bild hoch", "Das Bild muss mindestens 350px in der Breite haben.")
            return
        process_and_display_image(image)
    elif filename.lower().endswith(('.svg', '.pdf', '.ai')):
        output_path = f"{os.path.splitext(filename)[0]}.jpeg"
        vector_to_jpeg.convert_file(filename, output_path)
        if os.path.exists(output_path):
            image = Image.open(output_path)
            if image.width < 350:
                messagebox.showerror("Bitte laden Sie ein größeres Bild hoch", "Das Bild muss mindestens 350px in der Breite haben.")
                return
            process_and_display_image(image)

def process_and_display_image(image):
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
        background.paste(image, image.split()[-1])
        image = background
    image = image.convert('RGB')
    filename = f"{os.path.splitext(filename)[0]}_converted.jpg"
    image.save(filename)
    img = ImageTk.PhotoImage(image)
    image_label.config(image=img)
    image_label.image = img

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

def process_image_thread(image, reference_measure_cm, customer_data, save_customer_data, ref_type):
    try:
        calculation_data = rail_price = error = None
        processed_pil_image, output_string, total_width, total_height = image_processor.process_image(image, reference_measure_cm, ref_type)
        processed_pil_image = processed_pil_image.filter(ImageFilter.GaussianBlur(radius=0.0))
        _, img_jpg = cv2.imencode('.jpg', cv2.cvtColor(np.array(processed_pil_image), cv2.COLOR_RGB2BGR))
        image_data = str(base64.b64encode(img_jpg))

        heights = [float(line.split()[2]) for line in output_string.split('\n') if 'Element height' in line]
        
        if not heights:
            error = "No valid element heights found. Please ensure your image has detectable elements."
            return calculation_data, customer_data, rail_price, error

        total_price = sum(profile5s(height) for height in heights)

        invalid_heights, height_suggestions = validate_heights(heights)
        if invalid_heights:
            error = f"Ungültige Buchstabengröße: {invalid_heights}. Wir können Buchstaben von {height_suggestions['min_height']} cm bis {height_suggestions['max_height']} cm produzieren, Bitte passen Sie ihre Gesamtabmessung entsprechend an."
            return calculation_data, customer_data, rail_price, error

        width_valid, width_suggestions = validate_dimensions(total_width)
        if not width_valid:
            error = (f"Invalid total width: {total_width} cm. "
                     f"Valid range is {width_suggestions['min_width']} cm to {width_suggestions['max_width']} cm. "
                     f"Please adjust the height of your elements to fit within this range.")
            return calculation_data, customer_data, rail_price, error

        rail_price = calculate_railprice(total_width)
        
        price_including_rail = total_price + rail_price

        if connection is not None:
            calculation_data = {
                "calculation_data": output_string.split('\n'),
                "price_without_rail": total_price,
                "price_with_rail": price_including_rail,
                "reference_height": reference_measure_cm,
                "output_image": image_data
            }
            if save_customer_data:
                insert_calculation_result(connection, calculation_data, total_width, total_height, customer_data)

        return calculation_data, customer_data, rail_price, error

    except Exception as ex:
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

        image = request.json['image_data']
        image_type = request.json['image_type']
        reference_measure_cm = float(request.json['reference_measure_cm'])
        ref_type = request.json['ref_type']
        
        customer_data = {
            "company_name": request.json['company_name'],
            "customer_name": request.json['customer_name'],
            "customer_street": request.json['customer_street'],
            "customer_city": request.json['customer_city'],
            "customer_zipcode": request.json['customer_zipcode'],
            "customer_phone": request.json['customer_phone'],
            "customer_email": request.json['customer_email']
        }

        save_customer_data = request.json['save_customer_data']

        base64_decoded = base64.b64decode(image)
        
        if image_type.lower() in ['jpg', 'jpeg', 'png']:
            image = Image.open(io.BytesIO(base64_decoded))
        else:
            jpeg_base64 = vector_to_jpeg.convert_base64_to_jpeg(image, image_type)
            base64_decoded = base64.b64decode(jpeg_base64)
            image = Image.open(io.BytesIO(base64_decoded))
        
        if image.width < 350:
            raise ValueError("Uploaded logo must be at least 350px wide.")
        
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
            background.paste(image, image.split()[-1])
            image = background
        image = image.convert('RGB')
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        calculation_data, customer_data, rail_price, error = process_image_thread(image, reference_measure_cm, customer_data, save_customer_data, ref_type)

        if error is None:
            results['element_heights'] = []

            for element_data in calculation_data['calculation_data']:
                element_data = element_data.split(':')
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
            results['output_image'] = calculation_data['output_image']
            results['customer_data'] = customer_data
            
            message = {
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
                'error': error,
                'data': results
            }
            resp = jsonify(message)
            resp.status_code = 500
            return resp

    except Exception as ex:
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
            'error': str(traceback.format_exc()),
            'data': results
        }
        resp = jsonify(message)
        resp.status_code = 500
        return resp

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    try:
        data = request.json
        send_email(
            data['company_name'],
            data['customer_name'],
            data['customer_email'],
            data['customer_phone'],
            data['customer_street'],
            data['customer_zipcode'],
            data['customer_city']
        )
        return jsonify({"message": "Email sent successfully."}), 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({"message": "Failed to send email."}), 500

@app.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/', methods=["GET","POST"])
def html():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
