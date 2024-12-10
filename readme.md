# Autonomous Copilot Agent for Flight Simulation

This project simulates an autonomous copilot agent that collaborates with a human pilot in a flight simulator (X-Plane 11) during the take-off phase, particularly managing abnormal situations like engine failure after a bird strike. The agent uses a combination of machine learning (Random Forest classifier) and cognitive modeling (ACT-R) to determine the level of support needed by the pilot.

## Folder Structure

- **data/**: Contains the logged data from the flight simulations. 
  - **'cool'** in the filename refers to expert pilot data.
  - **'nul'** in the filename refers to novice pilot data.
  
- **xpc/**: The NASA XPlaneConnect plugin for setting up UDP communication between Python and the X-Plane 11 flight simulator.

- **actr.py**: A Python wrapper for interacting with the ACT-R cognitive architecture. 

- **annunciator.py**: A utility script for aural annunciations. This script listens to a queue from the main script (`engine_failure.py`) and returns the updated queue with messages, which are then executed on the main thread.

- **classifier.py**: Contains the logic for real-time classification using the Random Forest model. It is called by the main script to send flight log data and returns a classification (0 = novice, 1 = expert).

- **engine_failure.py**: The main script that sets up the ACT-R environment, initiates ACT-R experiments, and manages threads for other scripts.

- **engine_failure_model_mcgill_ai.lisp**: The ACT-R cognitive model written in Lisp, defining the memory and production rules for the agent.

- **log_takeoff.py**: A script for logging flight data from X-Plane 11 every 10 knots.

- **flightdir.py**: A script for displaying the flight director at 10° pitch angle during the takeoff.

- **manual_data_comparison.py**: A script for manually comparing two `.csv` files (e.g., "expert.csv" and "novice.csv") stored in the root folder.

- **random_forest_model_joblib**: The Random Forest model output from Scikit-learn (`joblib` format).

- **random_forest_model.pkl**: The Random Forest model output from the custom implementation (`pkl` format).

- **random_forest_scikit_training.py**: Random Forest Classification for T.A.R.S. Train a Random Forest classifier **using Scikit-Learn** Machine Learning library to predict flight data based on various features, used for comparison with our own implementation.

- **random_forest_training.py**: Our own Random Forest Classification for T.A.R.S. Train a Random Forest classifier to predict flight data based on various features. The classifier is implemented using decision trees, and it performs cross-validation to evaluate its performance. The script allows to experiment with different hyperparameters, including the number of trees, maximum depth, the minimum samples required to split a node, and cross-validation folds. Additionally, it provides the ability to experiment with different random seeds for reproducibility.

## Requirements

- Python 3.x
- Required Python libraries:
  - `sklearn` (for machine learning)
  - `numpy`, `pandas`, `matplotlib` (for data manipulation and visualization)
  - `xpc` (for X-Plane integration)
  - `joblib` (for loading the Random Forest model)
  - `pickle` (for loading the Random Forest model)
  - `pyttsx3` (for speech synthesis of the announces)

### Acknowledgements
This software uses [scikit-learn](https://scikit-learn.org/), which is licensed under the BSD 3-Clause License.
