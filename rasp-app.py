from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)

def stitch_images(images):
    # Convert images to OpenCV format
    cv_images = [cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR) for image in images]

    # Create a stitcher object
    try:
        stitcher = cv2.Stitcher_create()  # For OpenCV 3.x and above
    except AttributeError:
        stitcher = cv2.createStitcher(False)  # For OpenCV 2.x or if cv2.Stitcher_create is not available

    # Stitch images
    status, stitched = stitcher.stitch(cv_images)
    if status != cv2.Stitcher_OK:
        raise Exception("Image stitching failed: {}".format(status))
    return stitched

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stitch', methods=['POST'])
def stitch():
    images = request.files.getlist('images')
    if len(images) < 2:
        return "Please upload at least two images for stitching.", 400

    try:
        result = stitch_images(images)
        _, buffer = cv2.imencode('.jpg', result)
        return send_file(BytesIO(buffer), mimetype='image/jpeg', as_attachment=True, download_name='stitched.jpg')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
