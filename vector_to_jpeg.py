import base64
import tempfile
from PIL import Image
import cairosvg
from pdf2image import convert_from_path

def add_white_background(image):
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
        background.paste(image, image.split()[-1])
        image = background
    return image

def svg_to_jpeg(svg_data, output_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
        cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=temp_png.name)
        temp_png.flush()
        image = Image.open(temp_png.name)
        image = add_white_background(image)
        image = image.convert('RGB')
        image.save(output_path, 'JPEG')

def pdf_to_jpeg(pdf_data, output_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_data)
        temp_pdf.flush()
        images = convert_from_path(temp_pdf.name)
        if images:
            image = images[0]
            image = add_white_background(image)
            image = image.convert('RGB')
            image.save(output_path, 'JPEG')

def ai_to_jpeg(ai_data, output_path):
    pdf_to_jpeg(ai_data, output_path)  # Treat AI files as PDFs for conversion

def convert_base64_to_jpeg(base64_data, file_type):
    decoded_data = base64.b64decode(base64_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as temp_output_file:
        output_path = temp_output_file.name

    if file_type.lower() == 'svg':
        svg_to_jpeg(decoded_data.decode('utf-8'), output_path)
    elif file_type.lower() == 'pdf' or file_type.lower() == 'ai':
        pdf_to_jpeg(decoded_data, output_path)
    else:
        raise ValueError("Unsupported file type for base64 conversion")

    with open(output_path, "rb") as image_file:
        jpeg_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    return jpeg_base64

if __name__ == "__main__":
    # Example usage for base64 input
    with open("example.svg", "r") as image_file:
        base64_data = base64.b64encode(image_file.read().encode('utf-8')).decode('utf-8')

    jpeg_base64 = convert_base64_to_jpeg(base64_data, 'svg')
    print(jpeg_base64)
