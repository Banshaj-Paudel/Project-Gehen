import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
# Load the .h5 model
model = load_model('model.h5')

# Function to preprocess the image before passing it to the model
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # Normalize the image
    return x


# Function to make a prediction using the loaded model
# Function to make a prediction using the loaded model
def predict_dementia(input_image):
    input_image = preprocess_image(input_image)
    print("Input Image Shape:", input_image.shape)  # Debug statement
    prediction_result = model.predict(input_image)
    print("Prediction Result Shape:", prediction_result.shape)  # Debug statement

    # Get the predicted class index
    predicted_class_index = np.argmax(prediction_result)
    # Get the predicted class label
    predicted_class = ['Mild_Demented', 'Moderate_Demented', 'Non_Demented', 'Very_Mild_Demented'][predicted_class_index]

    # Get the percentage chance of dementia for each class
    percent_chances = {label: round(prob * 100, 2) for label, prob in zip(['Mild_Demented', 'Moderate_Demented', 'Non_Demented', 'Very_Mild_Demented'], prediction_result[0])}

    return predicted_class, percent_chances
