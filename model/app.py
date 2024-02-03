from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Load the .h5 model
h5model = load_model('model.h5')
img_size = [128, 128]
classes = ["Moderate_Demented", "Mild_Demented", "Non_Demented", "Very_Mild_Demented"]

def predict_dementia(image_path):
    # Load and preprocess the test image
    img = image.load_img(image_path, target_size=img_size)
    img_array = image.img_to_array(img)
    X_test = np.expand_dims(img_array, axis=0) / 255.0

    # Predict the class probabilities
    y_pred = h5model.predict(X_test)

    # Get the predicted class label
    predicted_class_index = np.argmax(y_pred)
    predicted_class = classes[predicted_class_index]

    # Get the percentage chance of dementia
    percent_chance = round(y_pred[0][predicted_class_index] * 100, 2)

    return percent_chance, predicted_class

@app.route('/')
def index():
   return 'This is the index page of API_Gehen. Send request to /predict endpoint with images'

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    try:
        # Check if the request contains an image
        if 'image' not in request.files:
            return jsonify({'error': 'No image sent'}), 400

        image_file = request.files['image']
        # Save the image to a temporary location on the server
        image_path = 'mri.jpg'
        image_file.save(image_path)

        # Make a prediction using the uploaded image
        percent_chance, predicted_class = predict_dementia(image_path)

        # Delete the temporary image file
        os.remove(image_path)

        return jsonify({'percent_chance': percent_chance, 'predicted_class': predicted_class}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
