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


# Truncate the df to have a fraction of the frames
threshold_frame = df["frame"].quantile(0.31)
# Truncate the DataFrame
df = df[df["frame"] <= threshold_frame].copy()


# post-oc computation of the Xcom = pelvis_pos + pelvis speed / sqrt(9.81 / pelvis_z[0] )
omega = np.sqrt((9.81 / df[df["agent_id"] == 1]["pelvis_z"].iloc[1]))

# Assuming time column exists (e.g., 'time') to compute actual velocity
dt = df["time"].diff()  # time differences
df["pelvis_vx"] = df["pelvis_x"].diff() / dt
df["pelvis_vy"] = df["pelvis_y"].diff() / dt

# # Compute Xcom
df["Xcom_x"] = df["pelvis_x"] + df["pelvis_vx"] / omega
df["Xcom_y"] = df["pelvis_y"] + df["pelvis_vy"] / omega

# Create figure and primary axis
SizeFactor = 1
fig, ax1 = plt.subplots(figsize=(SizeFactor * 8.1962 * 3, SizeFactor * 6.396))

# Styling constants
palette = {
    "pelvis": "blue",
    "Xcom": "purple",  # Changed to match your visual preference; use any color
    "r_foot": "#28C02D",
    "l_foot": "#D0420E",
}
CustomMarkerSize = 15
CustomFontname = "Arial"
CustomFontsize = 20  # Matched to the reference style
plt.rcParams["font.family"] = CustomFontname
plt.rcParams["font.size"] = CustomFontsize

# Plot the trajectories for agent_id == 1 (adjust if needed)
agent_id = 1
subset = df[(df["agent_id"] == agent_id) & (df["frame"] >= 2)]

# Plot pelvis position
ax1.plot(
    subset["pelvis_x"],
    subset["pelvis_y"],
    color=palette["pelvis"],
    linewidth=2.5,
    label="Pelvis",
)


sc = ax1.plot(
    subset["Xcom_x"],
    subset["Xcom_y"],
    color=palette["Xcom"],
    lw=0,
    marker="x",
    markersize=CustomMarkerSize,
)


# Plot heel positions
ax1.plot(
    subset["heel_right_x"],
    subset["heel_right_y"],
    color=palette["r_foot"],
    linewidth=1.5,
    alpha=0.1,
    marker="o",
    markersize=CustomMarkerSize,
    linestyle="",
    label="Heel Right",
)
ax1.plot(
    subset["heel_left_x"],
    subset["heel_left_y"],
    color=palette["l_foot"],
    linewidth=1.5,
    alpha=0.1,
    marker="o",
    markersize=CustomMarkerSize,
    linestyle="",
    label="Heel Left",
)

# Set labels and title
ax1.set_xlabel(
    "x [m]",
    fontname=CustomFontname,
    fontsize=CustomFontsize,
    labelpad=CustomFontsize / 2,
)
# ax1.set_ylabel(
#     "y [m]",
#     fontname=CustomFontname,
#     fontsize=CustomFontsize,
#     labelpad=CustomFontsize / 2,
# )

# Set equal aspect ratio, but allow the plot to adjust the limits
ax1.set_aspect("equal", adjustable="datalim")
# Axis limits and equal scaling
ax1.set_xlim(1.8, 6.6)
ax1.set_ylim(2.8, 3.95)


# Tick formatting

ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=6))
ticks_loc = ax1.get_xticks()
ax1.xaxis.set_major_locator(plt.FixedLocator(ticks_loc))
ax1.set_xticklabels(
    [str(round(x - 1.6, 2)) for x in ticks_loc], fontsize=CustomFontsize
)


ax1.yaxis.set_major_locator(plt.MaxNLocator(nbins=6))
ticks_loc = ax1.get_yticks()
ax1.yaxis.set_major_locator(plt.FixedLocator(ticks_loc))
ax1.set_yticklabels([str(round(y, 2)) for y in ticks_loc], fontsize=CustomFontsize)


# Grid
# ax1.grid(
#     visible=True,
#     which="major",
#     axis="x",
#     linestyle=":",
#     lw=0.8,
#     color="k",
#     alpha=0.4,
# )

# Legend
from matplotlib.lines import Line2D

custom_lines = [
    Line2D([0], [0], color=palette["pelvis"], lw=3),
    Line2D(
        [0], [0], color=palette["Xcom"], lw=0, marker="x", markersize=CustomMarkerSize
    ),
    Line2D(
        [0], [0], color=palette["r_foot"], lw=0, marker="o", markersize=CustomMarkerSize
    ),
    Line2D(
        [0], [0], color=palette["l_foot"], lw=0, marker="o", markersize=CustomMarkerSize
    ),
]
ax1.legend(
    handles=custom_lines,
    labels=["Pelvis", "$X_{CoM}$","Right foot", "Left foot", ],
    fontsize=int(CustomFontsize),
    bbox_to_anchor=(0.2, 0.4),
    frameon=False,
)

# Adjust layout
plt.tight_layout()
# Save the figure as SVG
plt.savefig("fig_Xcom_feet_trajectories_sim.svg", format="svg")

plt.show()
