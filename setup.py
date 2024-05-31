from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PIL', 'cv2', 'mysql', 'numpy', 'pdf2image', 'reportlab', 'schedule', 'svglib', 'tkinter'
        # Add any other packages that are not standard libraries and are used in your application
    ],
    'includes': [
        'image_processor', 'pricing', 'database', 'main'
        # Add any of your own modules that you want to include
    ],
    'plist': {
        'CFBundleName': 'YourAppName',
        'CFBundleDisplayName': 'YourAppName',
        'CFBundleGetInfoString': "Your application description",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
    },
}

setup(
    name='Lightvertise Kalkulator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
