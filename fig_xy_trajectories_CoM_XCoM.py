import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

simulation_file_name = "./corridor_HumanoidModelV0.sqlite"

# Connect to the database
conn = sqlite3.connect(simulation_file_name)
cursor = conn.cursor()

# Get all trajectory data ordered by frame
cursor.execute("SELECT * FROM trajectory_data ORDER BY frame")
data = cursor.fetchall()

# Get fps from metadata
cursor.execute("SELECT value FROM metadata WHERE key = 'fps'")
fps = float(cursor.fetchone()[0])

# Column indices based on your existing code:
# 0: frame, 1: agent_id, 9: pelvis_x, 10: pelvis_y, 11: pelvis_z

# Initialize an empty list to collect rows
data_rows = []

for row in data:
    frame = row[0]
    agent_id = row[1]
    pelvis_pos = np.array([row[9], row[10], row[11]])
    heel_right_pos = np.array([row[12], row[13], row[14]])
    heel_left_pos = np.array([row[15], row[16], row[17]])

    data_rows.append(
        {
            "frame": frame,
            "agent_id": agent_id,
            "time": frame / fps,
            "pelvis_x": pelvis_pos[0],
            "pelvis_y": pelvis_pos[1],
            "pelvis_z": pelvis_pos[2],
            "heel_right_x": heel_right_pos[0],
            "heel_right_y": heel_right_pos[1],
            "heel_left_x": heel_left_pos[0],
            "heel_left_y": heel_left_pos[1],
        }
    )

df = pd.DataFrame(data_rows)

# post-oc computation of the Xcom = pelvis_pos + pelvis speed / sqrt(9.81 / pelvis_z[0] )
omega = np.sqrt((9.81 / df[df["agent_id"] == 1]["pelvis_z"].iloc[1]))

# Assuming time column exists (e.g., 'time') to compute actual velocity
dt = df["time"].diff()  # time differences
df["pelvis_vx"] = df["pelvis_x"].diff() / dt
df["pelvis_vy"] = df["pelvis_y"].diff() / dt

# Compute Xcom
df["Xcom_x"] = df["pelvis_x"] + df["pelvis_vx"] / omega
df["Xcom_y"] = df["pelvis_y"] + df["pelvis_vy"] / omega


# Create figure and primary axis
fig, ax1 = plt.subplots(figsize=(7, 5))


# Plot the trajectories for agent_id == 1 (adjust if needed)
agent_id = 1
subset = df[(df["agent_id"] == agent_id) & (df["frame"] >= 2)]

# Plot pelvis position
ax1.plot(
    subset["pelvis_x"], subset["pelvis_y"], label="Pelvis", color="blue", linewidth=1.5
)

# Plot Xcom position
ax1.plot(
    subset["Xcom_x"],
    subset["Xcom_y"],
    label="Xcom",
    color="red",
    linewidth=1.5,
    linestyle="--",
)

# Plot heel positions
ax1.plot(
    subset["heel_right_x"],
    subset["heel_right_y"],
    label="Heel Right",
    color="green",
    linewidth=1.0,
    alpha=0.1,
    marker="o",
    markersize=8,
    linestyle="",
)
ax1.plot(
    subset["heel_left_x"],
    subset["heel_left_y"],
    label="Heel Left",
    color="red",
    linewidth=1.0,
    alpha=0.1,
    marker="o",
    markersize=8,
    linestyle="",
)

# Set labels and title
ax1.set_xlabel("X [m]")
ax1.set_ylabel("Y [m]")
# ax1.set_title(f"XY Trajectories of Pelvis, Xcom, and Heels (Agent {agent_id})")
ax1.legend()
ax1.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)
ax1.axis("equal")  # Ensure equal scaling for x and y

# Adjust layout and display
plt.tight_layout()
plt.show()
