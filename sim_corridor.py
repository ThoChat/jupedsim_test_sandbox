import pathlib
import matplotlib.pyplot as plt
import jupedsim as jps
import pedpy
from numpy.random import normal  # normal distribution of free movement speed
from shapely import Polygon

## Setup geometries
area = Polygon([(0, 0), (2, 0), (2, 10), (0, 10)])
walkable_area = pedpy.WalkableArea(area)
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


## Setup spawning area
spawning_area = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
pos_in_spawning_area = jps.distribute_until_filled(
    polygon=spawning_area,
    distance_to_agents=0.8,
    distance_to_polygon=0.3,
    seed=1,
)
num_agents = len(pos_in_spawning_area)
exit_area = Polygon([(0, 9), (2, 9), (2, 10), (0, 10)])


## Setup Simulation
trajectory_file = "corridor_HumanoidModelV0.sqlite"  # output file
simulation = jps.Simulation(
    model=jps.HumanoidModelV0(),
    geometry=area,
    trajectory_writer=jps.SqliteHumanoidTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

exit_id = simulation.add_exit_stage(exit_area.exterior.coords[:-1])
journey = jps.JourneyDescription([exit_id])
journey_id = simulation.add_journey(journey)

## Spawn agents
v_distribution = normal(1.34, 0.5, num_agents)

for pos, v0 in zip(pos_in_spawning_area, v_distribution):
    simulation.add_agent(
        jps.HumanoidModelV0AgentParameters(
            journey_id=journey_id,
            stage_id=exit_id,
            position=pos,
            head_position=pos,
            heel_right_position=(pos[0] + 0.20, pos[1]),
            heel_left_position=(pos[0] - 0.20, pos[1]),
            desiredSpeed=v0,
            height=1.7,
        )
    )

## run simulation
# print(isinstance(agent.model, jps.py_jupedsim.HumanoidModelV0State))
while simulation.agent_count() > 0:
    simulation.iterate()

## Import Sqlite with PedPy
from sqlite_loader_moded_pepy_fun import *

TrajectoryData = load_trajectory_from_jupedsim_sqlite(pathlib.Path(trajectory_file))
traj = TrajectoryData.data


# print(TrajectoryData.data[TrajectoryData.data["frame"] == 10])  # .iloc[0:5])


## Plotting results

# axes = pedpy.plot_walkable_area(walkable_area=walkable_area)
# axes.fill(*spawning_area.exterior.xy, color="lightgrey")
# axes.fill(*exit_area.exterior.xy, color="indianred")


# # Get unique agent IDs
# unique_agent_ids = traj["id"].unique()

# # Create a colormap
# cmap = plt.get_cmap("viridis", len(unique_agent_ids))

# # Initialize a counter for the color index
# color_index = 0

# for agent_id in traj["id"].unique():
#     agent_data = traj[traj["id"] == agent_id]
#     color = cmap(color_index)
#     # Move to the next color index
#     color_index += 1

#     # Position
#     axes.plot(
#         agent_data["x"],
#         agent_data["y"],
#         label=f"Head of Agent {agent_id}",
#         color=color,
#     )
#     # head position
#     axes.plot(
#         agent_data["head_pos_x"], agent_data["head_pos_y"], alpha=0.3, color=color
#     )
#     # heel right position
#     axes.plot(
#         agent_data["heel_right_pos_x"],
#         agent_data["heel_right_pos_y"],
#         alpha=0.3,
#         color=color,
#     )
#     # heel left position
#     axes.plot(
#         agent_data["heel_left_pos_x"],
#         agent_data["heel_left_pos_y"],
#         alpha=0.3,
#         color=color,
#     )

# axes.set_xlabel("x/m")
# axes.set_ylabel("y/m")
# axes.set_aspect("equal")
# plt.show()


# # Plot y_position of right and left heel as a function of frames on the same figure
# fig, axs = plt.subplots(1, 3, figsize=(15, 6))  # Two subplots

# for agent_id in traj["id"].unique():
#     agent_data = traj[traj["id"] == agent_id]

#     # Y-Position Subplot
#     axs[0].plot(
#         agent_data["frame"],
#         agent_data["heel_right_pos_y"],
#         label=f"Right Heel, Agent {agent_id}",
#         ls="-",
#     )
#     axs[0].plot(
#         agent_data["frame"],
#         agent_data["heel_left_pos_y"],
#         label=f"Left Heel, Agent {agent_id}",
#         ls="--",
#     )
#     axs[0].plot(
#         agent_data["frame"],
#         agent_data["head_pos_y"],
#         label=f"Head, Agent {agent_id}",
#         ls=":",
#         alpha=0.5,
#     )

#     # X-Position Subplot
#     axs[1].plot(
#         agent_data["frame"],
#         agent_data["heel_right_pos_x"],
#         label=f"Right Heel, Agent {agent_id}",
#         ls="-",
#     )
#     axs[1].plot(
#         agent_data["frame"],
#         agent_data["heel_left_pos_x"],
#         label=f"Left Heel, Agent {agent_id}",
#         ls="--",
#     )
#     axs[1].plot(
#         agent_data["frame"],
#         agent_data["head_pos_x"],
#         label=f"Head, Agent {agent_id}",
#         ls=":",
#         alpha=0.5,
#     )

#     # X-Y Subplot
#     axs[2].plot(
#         agent_data["heel_right_pos_x"],
#         agent_data["heel_right_pos_y"],
#         label=f"Right Heel, Agent {agent_id}",
#         ls="-",
#     )
#     axs[2].plot(
#         agent_data["heel_left_pos_x"],
#         agent_data["heel_left_pos_y"],
#         label=f"Left Heel, Agent {agent_id}",
#         ls="--",
#     )
#     axs[2].plot(
#         agent_data["head_pos_x"],
#         agent_data["head_pos_y"],
#         label=f"Head, Agent {agent_id}",
#         ls=":",
#         alpha=0.5,
#     )

# # Y-Position Subplot Configuration
# axs[0].set_title("Y-Positions")
# axs[0].set_xlabel("Frames")
# axs[0].set_ylabel("Y-Position (m)")
# axs[0].legend()
# axs[0].grid(True)

# # X-Position Subplot Configuration
# axs[1].set_title("X-Position")
# axs[1].set_xlabel("Frames")
# axs[1].set_ylabel("X-Position (m)")
# axs[1].legend()
# axs[1].grid(True)

# # X-Position Subplot Configuration
# axs[2].set_title("X-Y")
# axs[2].set_xlabel("X-Positions (m)")
# axs[2].set_ylabel("Y-Positions (m)")
# # axs[2].legend()
# axs[2].grid(True)
# axs[2].set_aspect("equal")

# plt.tight_layout()  # Adjust subplots to fit the figure area
# plt.show()
