import os
import re
import math
import pandas as pd
import matplotlib.pyplot as plt
from random import randrange
from random import  seed
import joblib
import argparse

DEFAULT_SEED = 42


def get_headers(file):
    try:
        # Open the file and read its content
        with open(file, "r") as file:
            content = file.read()

        # Use regex to extract the content inside the brackets
        match = re.search(r"\[(.*?)\]", content)
        if match:
            # Split the string into a list of individual strings
            extracted_list = match.group(1).split(", ")

        # Print the result
        return extracted_list
    except FileNotFoundError:
        print("The file was not found.")


def read_and_label_data(file):
    global headers
    try:
        if "cool" in file:
            label = 1  # Expert -> 1
        elif "nul" in file:
            label = 0  # Novice -> 0

        # Read the CSV file without headers and without naming columns initially
        df = pd.read_csv(file, header=None, names=None)

        # Add the numerical label to the dataset
        df["Label"] = label

        # Remove the first row if it's likely the header (i.e., non-numeric values)
        # This assumes that the header contains non-numeric values that can be filtered out
        df = df[~df.applymap(lambda x: isinstance(x, str)).any(axis=1)]  # Removes rows with string values

        return df
    except FileNotFoundError:
        print(f"The file {file} was not found.")
        return None


def pre_processing():
    """Label data, and combine all files in one dataset"""
    global headers, final_dataset, no_label_dataset
    file = "data/data.txt"
    headers = get_headers(file)
    current_dir = os.path.dirname(__file__)
    data_folder = os.path.join(current_dir, "data")

    datasets1 = []
    #datasets2 = []

    for file_name in os.listdir(data_folder):
        if file_name.endswith(".csv"):  # Filter only .csv files
            file_path = os.path.join(data_folder, file_name)
            labeled_data = read_and_label_data(file_path)  # Process the file
            if labeled_data is not None:
                datasets1.append(labeled_data)
                #datasets2.append(labeled_data.drop("Label", axis=1))  # Remove label for no-label dataset

    # Combine all labeled datasets into a single DataFrame
    final_dataset = pd.concat(datasets1, ignore_index=True)
    #no_label_dataset = pd.concat(datasets2, ignore_index=True)

    return final_dataset


def lr_split(index, value, dataset):
    """Create left and right subtrees"""
    left, right = list(), list()
    for row in dataset:
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    return left, right


def get_split(dataset, num_features):
    """Select the best feature to split on"""
    labels = ["Novice", "Expert"]
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    features = list()
    numeric_data = [row[:-1] for row in dataset]
    while len(features) < num_features:  # Randomly select features to split on
        index = randrange(len(dataset[0]) - 1)  # Randomly pick a feature index
        if index not in features:
            features.append(index)
    for index in features:
        for row in dataset:
            groups = lr_split(index, row[index], dataset)  # Split based on selected feature
            gini = gini_index(groups, labels)  # Calculate Gini index for the split
            if gini < b_score:  # If this is the best Gini score so far, keep track of it
                b_index, b_value, b_score, b_groups = index, row[index], gini, groups
    return {'index': b_index, 'value': b_value, 'groups': b_groups}


def split(node, max_depth, min_samples_split, num_features, depth):
    """Recusrsively split internal nodes until max_depth reached
    or min sample split size reached"""
    left, right = node['groups']
    del (node['groups'])
    # check for a no split
    if not left or not right:
        node['left'] = node['right'] = make_terminal(left + right)
        return
    # check for max depth
    if depth >= max_depth:
        node['left'], node['right'] = make_terminal(left), make_terminal(right)
        return
    # process left child
    if len(left) <= min_samples_split:
        node['left'] = make_terminal(left)
    else:
        node['left'] = get_split(left, num_features)
        split(node['left'], max_depth, min_samples_split, num_features, depth + 1)
    # process right child
    if len(right) <= min_samples_split:
        node['right'] = make_terminal(right)
    else:
        node['right'] = get_split(right, num_features)
        split(node['right'], max_depth, min_samples_split, num_features, depth + 1)


def gini_index(groups, labels):
    """Compute weighted Gini index: evaluate split by measuring imppurity"""
    # Count all samples at the split point
    instances = float(sum([len(group) for group in groups]))

    # Sum weighted Gini index for each group
    gini = 0.0
    for group in groups:
        size = float(len(group))
        # Avoid division by zero
        if size == 0:
            continue
        score = 0.0
        # Score the group based on the score for each class
        for label in labels:
            p = [row[-1] for row in group].count(label) / size
            score += p * p
        # Weight the group score by its relative size
        gini += (1.0 - score) * (size / instances)
    return gini


def make_terminal(node):
    outs = [row[-1] for row in node]
    return max(set(outs), key=outs.count)


def build_tree(d_train, max_depth, min_samples_split, num_features):
    root = get_split(d_train, num_features)
    split(root, max_depth, min_samples_split, num_features, 1)
    return root


def random_forest(d_train, d_test, max_depth, min_samples_split, sample_size, num_trees, num_features):
    """Rnadom Forest"""
    global trees
    #print(f"Training dataset size before building trees: {len(d_train)}")
    trees = list()
    for i in range(num_trees):
        sample = subsample(d_train, sample_size)
        #print(f"Sample size for tree {i + 1}: {len(sample)}")
        if not sample:
            raise ValueError(f"Sample is empty in random_forest() at iteration {i}")
        tree = build_tree(sample, max_depth, min_samples_split, num_features)
        trees.append(tree)
    predictions = [bagging_predict(trees, row) for row in d_test]
    return predictions


def cross_validation_split(dataset, k_folds):
    """Implement the splitting portion of k-folds cross-validation"""
    d_split = []
    d_copy = dataset.values.tolist()
    fold_size = len(dataset) // k_folds  # Integer division to get fold size
    remainder = len(dataset) % k_folds  # This will give us the number of folds that need one extra item

    #print(f"Fold size: {fold_size}, Remainder: {remainder}")
    #print(f"Initial dataset size: {len(d_copy)}")

    for i in range(k_folds):
        fold = list()
        # For the first 'remainder' folds, we add one extra item
        fold_size_with_remainder = fold_size + 1 if i < remainder else fold_size
        #print(f"Processing fold {i + 1}, fold size: {fold_size_with_remainder}")

        while len(fold) < fold_size_with_remainder:
            # If the list is empty, break early
            if not d_copy:
                print("d_copy is empty, breaking out of the loop")
                break
            index = randrange(len(d_copy))  # Random index to pop
            fold.append(d_copy.pop(index))

        #print(f"Fold {i + 1} contains: {fold}")
        d_split.append(fold)

    #print(f"Remaining items in d_copy after splitting: {len(d_copy)}")
    return d_split


def subsample(dataset, ratio):
    """Randomly sample with replacement from the dataset"""
    sample = list()
    n_sample = round(len(dataset) * ratio)
    while len(sample) < n_sample:
        index = randrange(len(dataset))
        sample.append(dataset[index])
    return sample


def bagging_predict(trees, row):
    """Make predictions from a list of bagged trees"""
    predictions = [predict(tree, row) for tree in trees]
    return max(set(predictions), key=predictions.count)


def predict(node, row):
    """Make a prediction/classification guess with a decision tree"""
    if row[node['index']] < node['value']:
        if isinstance(node['left'], dict):
            return predict(node['left'], row)
        else:
            return node['left']
    else:
        if isinstance(node['right'], dict):
            return predict(node['right'], row)
        else:
            return node['right']


def evaluate(dataset, k_folds, num_trees, num_features, min_samples_split, sample_size, max_depth):
    """Run and Evaluate random forest"""
    global final_dataset
    folds = cross_validation_split(dataset, k_folds)
    #print(f"Number of folds: {len(folds)}")
    scores = []
    for fold in folds:
        train_set = list(folds)
        train_set.remove(fold)
        # Flatten the train_set correctly
        train_set = [list(row) for fold in train_set for row in fold]

        test_set = list()
        for row in fold:
            row_copy = list(row)
            test_set.append(row_copy)
            row_copy[-1] = None

        predicted = random_forest(train_set, test_set, max_depth, min_samples_split, sample_size, num_trees, num_features)
        actual = [row[-1] for row in fold]
        accuracy_score = accuracy(actual, predicted)
        scores.append(accuracy_score)
    return scores


def accuracy(true_value, prediction):
    """Evaluate the accuracy of the prediction"""
    correct = sum([1 for a, p in zip(true_value, prediction) if a == p])  # Count correct predictions
    total = len(true_value)  # Total number of predictions
    return (correct / total)*100.00  # Accuracy as a ratio


def save_model(model, filename):
    """Save model for real time application"""
    with open(filename, 'wb') as f:
        joblib.dump(model, f)
    print(f"Model saved to {filename}")


def load_model(filename):
    """Load saved model"""
    with open(filename, 'rb') as f:
        model = joblib.load(f)
    print(f"Model loaded from {filename}")
    return model


def real_time_prediction(flight_data):
    """Real time random forest classification"""
    # Load the trained model
    model = load_model("random_forest_model.pkl")

    # Assuming flight_data is in the same format as the training data (with features)
    prediction = bagging_predict(model, flight_data)
    return prediction


def parse_arguments():
    """ Argument parsing for flexible parameter passing"""
    parser = argparse.ArgumentParser(description="Random Forest for Flight Data Classification")

    # Adding arguments with default values
    parser.add_argument('--min_samps', type=int, default=5, help='Minimum samples required to split a node (default=4)')
    parser.add_argument('--k_folds', type=int, default=4, help='Number of folds for cross-validation (default=4)')
    parser.add_argument('--n_trees', type=int, default=15, help='Number of trees in the random forest (default=12)')
    parser.add_argument('--m_depth', type=int, default=12, help='Maximum depth of the trees (default=12)')
    parser.add_argument('--sp_size', type=float, default=0.65, help='Sample size for building trees (default=0.65)')
    parser.add_argument('--seeds', type=int, nargs='+', default=[DEFAULT_SEED], help='List of seeds for random number generation (default=[42])')

    return parser.parse_args()


def main():
    global trees
    args = parse_arguments()
    dataset = pre_processing()
    num_features = int(math.sqrt(len(headers)))
    min_samples_split = args.min_samps
    k_folds = args.k_folds
    num_trees = args.n_trees
    max_depth = args.m_depth
    sample_size = args.sp_size
    seeds = args.seeds
    mean_accuracies = []

    for s in seeds:
        # Set the seed for reproducibility
        seed(s)

        print(f"Running with seed: {s}")

        # Evaluate with the current seed
        scores = evaluate(dataset, k_folds, num_trees, num_features, min_samples_split, sample_size, max_depth)
        mean_accuracy = sum(scores) / float(len(scores))
        print(f"Scores: {scores}")
        mean_accuracies.append(mean_accuracy)
        print('K-Folds: %d' % k_folds)
        print('Number of Trees: %d' % num_trees)
        print('Max depth: %d' % max_depth)
        print('Minimum Sample split: %d' % min_samples_split)
        print('Sample size: %f' % sample_size)
        print(f"Mean Accuracy for seed {s}: {mean_accuracy:.3f}%")
        print("------------------------------------------------------")

    # After training, save the model
    model_filename = "random_forest_model.pkl"
    save_model(trees, model_filename)

    # Plotting the results
    plt.figure(figsize=(8, 6))
    plt.plot(seeds, mean_accuracies, marker='o', linestyle='-', color='b')
    plt.title('Effect of Different Seeds on Accuracy')
    plt.xlabel('Seed Value')
    plt.ylabel('Mean Accuracy (%)')
    plt.grid(True)
    plt.show()


"""  
    #
    scores = evaluate(dataset, k_folds, num_trees, num_features, min_samples_split, sample_size, max_depth)
    mean_accuracy = sum(scores) / float(len(scores))
    #print('Trees: %d' % num_trees)
    print('K-Folds: %d' % k_folds)
    print('Number of Trees: %d' % num_trees)
    print('Max depth: %d' % max_depth)
    print('Minimum Sample split: %d' % min_samples_split)
    print('Sample size: %f' % sample_size)
    print('Scores: %s' % scores)
    print('Mean Accuracy: %.3f%%' % mean_accuracy)
    #num_trees_list.append(num_trees)
    #mean_accuracy_list.append(mean_accuracy)
    # After training, save the model
    model_filename = "random_forest_model.pkl"
    save_model(trees, model_filename)
    # Plotting the results

    plt.figure(figsize=(8, 6))
    plt.plot(k_folds_values, mean_accuracy_list, marker='o', linestyle='-', color='b')
    plt.title('Effect of K-Folds on Accuracy (Fixed Number of Trees)')
    plt.xlabel('K-folds')
    plt.ylabel('Mean Accuracy (%)')
    plt.grid(True)
    plt.xticks(range(1, 16))  # Show ticks from 1 to 15 for number of trees
    plt.yticks([i for i in range(0, 101, 10)])  # Set y-axis from 0% to 100%
    plt.show()
"""
if __name__ == "__main__":
    main()