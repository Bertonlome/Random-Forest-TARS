import os
import re
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

def get_headers(file):
    """Extract headers from a given file."""
    try:
        with open(file, "r") as f:
            content = f.read()
        match = re.search(r"\[(.*?)\]", content)
        if match:
            return match.group(1).split(", ")
        return []
    except FileNotFoundError:
        print("The file was not found.")
        return []

def read_and_label_data(file):
    """Read and label the data based on the file name."""
    try:
        label = 1 if "cool" in file else 0  # Expert=1, Novice=0
        df = pd.read_csv(file, header=None)
        df["Label"] = label
        return df
    except FileNotFoundError:
        print(f"The file {file} was not found.")
        return None

def pre_processing():
    """Load and label all datasets."""
    current_dir = os.path.dirname(__file__)
    data_folder = os.path.join(current_dir, "data")
    datasets = []
    for file_name in os.listdir(data_folder):
        if file_name.endswith(".csv"):
            file_path = os.path.join(data_folder, file_name)
            labeled_data = read_and_label_data(file_path)
            if labeled_data is not None:
                datasets.append(labeled_data)
    return pd.concat(datasets, ignore_index=True)

def main():
    # Load and preprocess the data
    dataset = pre_processing()
    headers = get_headers("data/data.txt")
    X = dataset.iloc[:, :-1]  # Features
    y = dataset["Label"]      # Labels

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the Random Forest model
    model = RandomForestClassifier(n_estimators=10, max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

    # Cross-validation
    scores = cross_val_score(model, X, y, cv=4)
    print(f"Cross-Validation Accuracy: {scores.mean() * 100:.2f}%")

    # Save the model
    joblib.dump(model, "random_forest_model.joblib")
    print("Model saved to random_forest_model.joblib")

    import matplotlib.pyplot as plt

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    features = dataset.columns[:-1]  # Assuming last column is the label

    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(range(len(importances)), features[indices], rotation=90)
    plt.tight_layout()
    plt.show()


    # Plot Cross-Validation Scores
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, len(scores) + 1), scores * 100, marker="o", linestyle="-", color="b")
    plt.title("Cross-Validation Scores")
    plt.xlabel("Fold")
    plt.ylabel("Accuracy (%)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
