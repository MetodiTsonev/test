import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import cv2
import sqlite3


app = Flask(__name__)
camera = None  # Global variable to hold the camera object
DATABASE = os.path.join(os.getcwd(), 'databases', 'my_db.sqlite')


def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def capture_photo():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        # Generate a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_name = f'captured_photo_{timestamp}.jpg'
        cv2.imwrite(image_name, frame)

        with open(image_name, 'rb') as img_file:
            image_data = img_file.read()

        # Retrieve coordinates from the POST request
        data = request.get_json()
        x_coord = data.get('x', 0)
        y_coord = data.get('y', 0)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO MouseData (x_coordinate, y_coordinate, image_data) VALUES (?, ?, ?)",
                       (x_coord, y_coord, sqlite3.Binary(image_data)))
        conn.commit()
        conn.close()
        camera.release()
        camera = None
        return jsonify({'message': 'Photo captured and saved to the database'})
    else:
        return jsonify({'message': 'Failed to capture image'})


if __name__ == '__main__':
    app.run(debug=True)
