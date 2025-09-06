import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

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

# select only data from agent 1
values = agent_dict[1]

## pre-computation
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
speed = np.linalg.norm(velocities, axis=1)

# smoothing ising averaging rolling window
# Choose window size
window = 10

kernel = np.ones(window) / window

# Apply moving average
smoothed_speed = np.convolve(speed, kernel, mode="same")

# Align time to center between frames
time_center = (time[:-1] + time[1:]) / 2


# Create figure and primary axis
SizeFactor = 1
fig, ax1 = plt.subplots(figsize=(SizeFactor * 8.1962, SizeFactor * 6.396))
palette = {
    "speed": "#1A3D6B",
    "r_foot": "#28C02D",
    "l_foot": "#D0420E",
}
CustomFontname = "Arial"
CustomFontsize = 20
plt.rcParams["font.family"] = CustomFontname  # Set Legent font to CustomFont

# Plot pelvis speed on primary y-axis
ax1.plot(
    time_center,
    smoothed_speed,
    color=palette["speed"],
    lw=3,
)

# Create secondary y-axis for heel Z-coordinates
ax2 = ax1.twinx()

# Plot heel Z-coordinates on secondary y-axis

heel_right_z = np.array(values["heel_right_z"])
heel_left_z = np.array(values["heel_left_z"])
time = np.array(values["time"])

ax2.plot(
    time,
    heel_right_z,
    color=palette["r_foot"],
    linestyle="--",
    lw=3,
)
ax2.plot(time, heel_left_z, color=palette["l_foot"], linestyle="--", lw=3)


ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Pelvis Speed (m/s)")
ax1.tick_params(axis="y")
ax1.grid(True, alpha=0.3)

ax2.set_ylabel("Heel height (m)")
ax2.tick_params(axis="y")
ax2.grid(False)


# Styling
ax1.set_xlim((0, 4))
ax2.set_ylim((0, 0.5))

ax1.set_xlabel(
    "Time (s)",
    fontname=CustomFontname,
    fontsize=CustomFontsize,
    labelpad=CustomFontsize / 2,
    # fontstyle="italic",
)
ax1.set_ylabel(
    "Pelvis Speed (m/s)",
    fontname=CustomFontname,
    fontsize=CustomFontsize,
    labelpad=CustomFontsize / 2,
    # fontstyle="italic",
)

ax2.set_ylabel(
    "Heel height (m)",
    fontname=CustomFontname,
    fontsize=CustomFontsize,
    # fontstyle="italic",
)

ax1.xaxis.set_major_locator(mticker.MaxNLocator(nbins=6))  # reduice the number of ticks
ticks_loc = ax1.get_xticks()
ax1.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
ax1.set_xticklabels([str(round(x, 2)) for x in ticks_loc], fontsize=CustomFontsize)

ax1.yaxis.set_major_locator(mticker.MaxNLocator(nbins=8))
ticks_loc = ax1.get_yticks()
ax1.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
ax1.set_yticklabels([str(round(y, 2)) for y in ticks_loc], fontsize=CustomFontsize)


new_ticks_ax2 = np.arange(0.05, 0.30, 0.05)
ax2.set_yticks(new_ticks_ax2)
ax2.set_yticklabels([str(round(y, 2)) for y in new_ticks_ax2], fontsize=CustomFontsize)

ax1.grid(
    visible=True,
    which="major",
    axis="both",
    linestyle=":",
    lw=0.5,
    color="k",
    alpha=0.3,
)

# Title and legend


from matplotlib.lines import Line2D

custom_lines = [
    Line2D(
        [0],
        [0],
        color=palette["speed"],
        lw=3,
    ),
    Line2D([0], [0], color=palette["r_foot"], lw=3, linestyle="--"),
    Line2D([0], [0], color=palette["l_foot"], lw=3, linestyle="--"),
]
ax2.legend(
    handles=custom_lines,
    labels=["Pelvis Speed", "Right foot", "Left foot"],
    fontsize=int(CustomFontsize * 0.7),
    bbox_to_anchor=(0.33, 1),
)

plt.tight_layout()
plt.show()
