import numpy as np
from joblib import load
from sklearn.ensemble import RandomForestClassifier  # Explicit import for clarity
import os

# Function to classify new data
def classify_new_data(input_data):
    """
    Classifies new data using the pre-trained Random Forest model.

    Parameters:
    - input_data: A list or NumPy array of feature values for the new data point.

    Returns:
    - prediction: The predicted class label.
    """
    try:
        # Load the saved Random Forest model
        # Get the absolute path of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "random_forest_model.joblib")
        model = load(model_path)
        # Ensure the input data is in the correct shape
        input_data = np.array(input_data).reshape(1, -1)

        # Make a prediction
        prediction = model.predict(input_data)

        return prediction[0]  # Return the predicted class
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage of the classify_new_data function
def main(new_data):


    # Classify the new data
    predicted_class = classify_new_data(new_data)
    if predicted_class is not None:
        if predicted_class == 0:
            print(f"Predicted Class: NOVICE")
        else:
            print("Predicted Class: EXPERT")
'''
# Example input data (replace with actual feature values)
new_data = [190, 0.06619141104590934, 0.11402236234390394, 0.0,
            0.09719755051768182, 3.4675974969399745, 2.256969451904297,
            7.62939453125e-05, 1.7045223712921143]
main(new_data)
'''