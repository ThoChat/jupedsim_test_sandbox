import sqlite3
import numpy as np
import matplotlib.pyplot as plt

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

# Organize data by agent
agent_dict = {}
for row in data:
    frame = row[0]
    agent_id = row[1]
    pelvis_pos = np.array([row[9], row[10], row[11]])
    heel_right_pos = np.array([row[12], row[13], row[14]])
    heel_left_pos = np.array([row[15], row[16], row[17]])

    if agent_id not in agent_dict:
        agent_dict[agent_id] = {
            "time": [],
            "pelvis_pos": [],
            "heel_right_z": [],
            "heel_left_z": [],
        }
    agent_dict[agent_id]["time"].append(frame / fps)
    agent_dict[agent_id]["pelvis_pos"].append(pelvis_pos)
    agent_dict[agent_id]["heel_right_z"].append(heel_right_pos[2])
    agent_dict[agent_id]["heel_left_z"].append(heel_left_pos[2])

# Create figure and primary axis
fig, ax1 = plt.subplots(figsize=(7, 5))

for agent_id, values in agent_dict.items():
    time = np.array(values["time"])
    agent_pelvis_pos = np.array(values["pelvis_pos"])

    # Remove the first frame to avoid division by zero
    time = time[1:]

    # Calculate velocity vectors between frames
    deltas = np.diff(agent_pelvis_pos, axis=0)
    time_deltas = np.diff(time)
    time_deltas = time_deltas[:, np.newaxis]  # To broadcast correctly

    # Adjust deltas length to match the number of frames
    deltas = deltas[1:]

    velocities = deltas / time_deltas
    speeds = np.linalg.norm(velocities, axis=1)

    # Align time to center between frames
    time_center = (time[:-1] + time[1:]) / 2

    # Plot pelvis speed on primary y-axis
    ax1.plot(time_center, speeds, label=f"Agent {agent_id} - Speed", alpha=0.8)

# Create secondary y-axis for heel Z-coordinates
ax2 = ax1.twinx()

# Plot heel Z-coordinates on secondary y-axis
for agent_id, values in agent_dict.items():
    heel_right_z = np.array(values["heel_right_z"])
    heel_left_z = np.array(values["heel_left_z"])
    time = np.array(values["time"])

    ax2.plot(
        time,
        heel_right_z,
        color="C0",
        linestyle="--",
        alpha=0.6,
        linewidth=1,
    )
    ax2.plot(time, heel_left_z, color="C1", linestyle="--", alpha=0.6, linewidth=1)

# Styling
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Pelvis Speed (m/s)")
ax1.tick_params(axis="y")
ax1.grid(True, alpha=0.3)

ax2.set_ylabel("Heel Z-Position (m)")
ax2.tick_params(axis="y")
ax2.grid(False)
ax2.set_ylim((0, 0.5))


# Title and legend
plt.title("Pelvis Speed and Heel Z-Position Over Time for Each Agent")
ax1.legend(loc="upper left")
# Create custom legend for the secondary axis
from matplotlib.lines import Line2D

custom_lines = [
    Line2D([0], [0], color="C0", lw=2, label="Pelvis Speed"),
    Line2D([0], [0], color="C0", lw=2, linestyle="--", label="Right Heel Z"),
    Line2D([0], [0], color="C1", lw=2, linestyle="--", label="Left Heel Z"),
]
ax2.legend(handles=custom_lines, loc="upper right")

plt.tight_layout()
plt.show()
