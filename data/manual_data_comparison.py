import pandas as pd
import matplotlib.pyplot as plt

# Load CSV files for expert and novice
expert_data = pd.read_csv("expert.csv", header=None)
novice_data = pd.read_csv("novice.csv", header=None)

# Assign column names for better readability
columns = ["Speed", "aileron_rms", "elevator_rms", "rudder_rms", "deviation_rms", 
           "pitch_rms", "retract_flaps_reaction_time", "retract_gear_reaction_time", "rotation_reaction_time"]
expert_data.columns = novice_data.columns = columns

# Ensure speed alignment for both datasets (if speeds differ, use an inner join)
merged_data = pd.merge(
    expert_data, novice_data, on="Speed", suffixes=("_expert", "_novice")
)

# Plot differences for each value column
for col in columns[1:]:
    plt.figure(figsize=(10, 5))
    plt.plot(merged_data["Speed"], merged_data[f"{col}_expert"], label=f"{col} (Expert)", marker="o")
    plt.plot(merged_data["Speed"], merged_data[f"{col}_novice"], label=f"{col} (Novice)", marker="x")
    plt.title(f"Comparison of {col} between Expert and Novice")
    plt.xlabel("Speed")
    plt.ylabel(col)
    plt.legend()
    plt.grid()
    plt.show()
