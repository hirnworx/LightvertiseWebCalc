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
from image_processor import process_image
import vector_to_jpeg
# from pricing import profile5s, calculate_railprice
from pricing_logic_letters import letter_price_calculator, calculate_railprice
from pricing_logic_lightbox import lk_price
from database.db_operations import create_table, insert_calculation_result, insert_error_form_submission, insert_lightbox_calculation_result
from validator import validate_heights, validate_dimensions
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize filename as None
filename = None

# Create tables in the database
try:
    create_table()
except Exception as e:
    print(f"Fehler bei der Erstellung der Tabellen: {e}")

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
        if image.width < 250:
            messagebox.showerror("Bitte laden Sie ein größeres Bild hoch", "Das Bild muss mindestens 250px in der Breite haben.")
            return
        process_and_display_image(image)
    elif filename.lower().endswith(('.svg', '.pdf', '.ai')):
        output_path = f"{os.path.splitext(filename)[0]}.jpeg"
        vector_to_jpeg.convert_file(filename, output_path)
        if os.path.exists(output_path):
            image = Image.open(output_path)
            if image.width < 350:
                messagebox.showerror("Bitte laden Sie ein größeres Bild hoch", "Das Bild muss mindestens 250px in der Breite haben.")
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
        messagebox.showerror("Ungültige Eingabe", "Ungültiger Höhenwert. Bitte geben Sie eine gültige Nummer ein.")

def process_image_thread(image, reference_measure_cm, customer_data, save_customer_data, ref_type, letter_type):
    calculation_data = rail_price = error = None
    try:
        processed_pil_image, output_string, total_width, total_height, invalid_heights = process_image(image, reference_measure_cm, ref_type)
        processed_pil_image = processed_pil_image.filter(ImageFilter.GaussianBlur(radius=0.0))
        _, img_jpg = cv2.imencode('.jpg', cv2.cvtColor(np.array(processed_pil_image), cv2.COLOR_RGB2BGR))
        image_data = str(base64.b64encode(img_jpg))

        heights = [float(line.split()[2]) for line in output_string.split('\n') if 'Element height' in line]
        
        if not heights:
            error = "Keine gültigen Elementhöhen gefunden. Bitte stellen Sie sicher, dass Ihr Bild erkennbare Elemente enthält."
            return calculation_data, customer_data, rail_price, error

        if invalid_heights:
            invalid_heights_str = ', '.join(f"{height:.2f} cm" for height in invalid_heights)
            error = f"Leider sind einige Elemente in Ihrem Logo zu klein um Sie als Leuchtbuchstaben zu produzieren. Hier die Elemente von links nach rechts: {invalid_heights_str})."
            return calculation_data, customer_data, rail_price, error

        # total_price = sum(profile5s(height) for height in heights)
        total_price = sum(letter_price_calculator(height, letter_type) for height in heights)

        width_valid, width_suggestions = validate_dimensions(total_width)
        if not width_valid:
            error = (f"Ungültige Gesamtbreite: {total_width} cm. "
                     f"Gültiger Bereich ist {width_suggestions['min_width']} cm bis {width_suggestions['max_width']} cm. "
                     f"Bitte passen Sie die Höhe Ihrer Elemente an, um innerhalb dieses Bereichs zu bleiben.")
            return calculation_data, customer_data, rail_price, error

        rail_price = calculate_railprice(total_width)
        
        price_including_rail = total_price + rail_price

        calculation_data = {
            "calculation_data": output_string.split('\n'),
            "price_without_rail": total_price,
            "price_with_rail": price_including_rail,
            "reference_height": reference_measure_cm,
            "output_image": image_data
        }

        if save_customer_data:
            insert_calculation_result(calculation_data, total_width, total_height, letter_type, customer_data)

        return calculation_data, customer_data, rail_price, error

    except ValueError as ex:
        # Handle specific known errors
        error = str(ex)
    except Exception as ex:
        # Handle any other unexpected errors
        error = "Es gab ein Problem bei der Verarbeitung Ihres Bildes. Bitte stellen Sie sicher, dass Ihr Bild die richtigen Anforderungen erfüllt."
        print("\n")
        print("------------------------------------------------")
        print("   FEHLER:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Fehler-Traceback ---------------")
        print(traceback.format_exc())
        print("------------------------------------------------")
        print("\n")

    return calculation_data, customer_data, rail_price, error

# Function to calculate the price for light box
def lightbox_calculate_price(width, height, type, lkw, customer_data, save_customer_data, upcharge_percent=80):
    try:
        final_price = error = None

        qcm = width * height  # Calculate square centimeters
        sqm = qcm / 10000     # Convert to square meters

        # Debugging print
        print(f"Width: {width} cm, Height: {height} cm, qcm: {qcm} cm², sqm: {sqm} m²")

        if qcm > 0:
            base_price = lk_price(qcm, type, lkw)
        else:
            base_price = 0
        
        if base_price == 0:
            print(f"Price NOT applicable for these dimensions -> Width: {width}, Height: {height}")
            return base_price, error
        
        # Apply upcharge to the base price
        final_price = base_price * sqm * (1 + upcharge_percent / 100)

        if save_customer_data:
            insert_lightbox_calculation_result(width, height, type, lkw, final_price, customer_data)  # Pass customer_data here

        return final_price, error

    except Exception as ex:
        error = traceback.format_exc()
        print("\n")
        print("------------------------------------------------")
        print("   FEHLER:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Fehler-Traceback ---------------")
        print(traceback.format_exc())
        print("------------------------------------------------")
        print("\n")

        return final_price, error

def update_image_label(tk_image):
    image_label.config(image=tk_image)
    image_label.image = tk_image
    max_width = 300

def reset_fields(event=None):
    global filename
    filename_label.config(text="Keine Datei ausgewählt")
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

        # print(data)

        image = request.json['image_data']
        image_type = request.json['image_type']
        reference_measure_cm = float(request.json['reference_measure_cm'])
        ref_type = request.json['ref_type']
        letter_type = request.json['letter_type']
        
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
        
        if image.width < 250:
            raise ValueError("Das hochgeladene Logo muss mindestens 250 Pixel breit sein.")
        
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
            background.paste(image, image.split()[-1])
            image = background
        image = image.convert('RGB')
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        calculation_data, customer_data, rail_price, error = process_image_thread(image, reference_measure_cm, customer_data, save_customer_data, ref_type, letter_type)

        if error is None and calculation_data is not None:
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
            results['letter_type'] = letter_type

            
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
            if error is None:
                error = "Ein unbekannter Fehler ist aufgetreten."
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
        print("   FEHLER:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Fehler-Traceback ---------------")
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

@app.route('/lightbox_calculation',methods=['POST'])
def lightbox_calculation():

    try:
        results = {}

        if len(request.form) > 0:
            data = json.loads(request.form['data'])
        else:
            data = request.json
        print(data)
        width = float(request.json['width'])
        height = float(request.json['height'])
        type = request.json['type']
        lkw = request.json['lkw']
        save_customer_data = request.json['save_customer_data']

        customer_data = {
            "company_name": request.json['company_name'],
            "customer_name": request.json['customer_name'],
            "customer_street": request.json['customer_street'],
            "customer_city": request.json['customer_city'],
            "customer_zipcode": request.json['customer_zipcode'],
            "customer_phone": request.json['customer_phone'],
            "customer_email": request.json['customer_email']
        }

        final_price, error = lightbox_calculate_price(width, height, type, lkw, customer_data, save_customer_data)

        if error == None:
            if final_price != 0:

                results['final_price'] = final_price
                results['width'] = width
                results['height'] = height
                results['type'] = type
                results['lkw'] = lkw
                results['customer_data'] = customer_data
                results['msg'] = None
                # print("results: ", results)
                
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
                results['final_price'] = final_price
                results['width'] = width
                results['height'] = height
                results['type'] = type
                results['lkw'] = lkw
                results['customer_data'] = customer_data
                results['msg'] = f"Price NOT applicable for these dimensions -> Width: {width}, Height: {height}"
                # print("results: ", results)
                
                message = {
                    'error': f"Price NOT applicable for these dimensions -> Width: {width}, Height: {height}",
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
        print("   FEHLER:- " + str(ex))
        print("------------------------------------------------")
        print("\n")
        print("---------------- Fehler-Traceback ---------------")
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

@app.route('/save_error_data', methods=['POST'])
def save_error_data():
    try:
        data = request.json
        insert_error_form_submission(data)  # no need to pass connection
        return jsonify({"message": "Daten erfolgreich gespeichert."}), 200
    except Exception as e:
        print(f"Fehler beim Speichern der Daten: {e}")
        return jsonify({"message": "Fehler beim Speichern der Daten."}), 500

@app.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/', methods=["GET","POST"])
def html():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
