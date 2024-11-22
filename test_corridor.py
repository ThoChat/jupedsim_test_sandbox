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
    distance_to_agents=3,
    distance_to_polygon=0.4,
    seed=1,
)
num_agents = len(pos_in_spawning_area)
exit_area = Polygon([(0, 8), (2, 8), (2, 10), (0, 10)])


## Setup Simulation
trajectory_file = "test_HumanoidModelV0.sqlite"  # output file
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
            desiredSpeed=v0,
        )
    )

## run simulation
while simulation.agent_count() > 0:
    simulation.iterate()

## Import Sqlite with PedPy
from sqlite_loader_moded_pepy_fun import *

TrajectoryData = load_trajectory_from_jupedsim_sqlite(pathlib.Path(trajectory_file))

# print(TrajectoryData.data[TrajectoryData.data["frame"] == 10])  # .iloc[0:5])


## Plotting results


axes = pedpy.plot_walkable_area(walkable_area=walkable_area)
axes.fill(*spawning_area.exterior.xy, color="lightgrey")
axes.fill(*exit_area.exterior.xy, color="indianred")

traj = TrajectoryData.data


# Get unique agent IDs
unique_agent_ids = traj["id"].unique()

# Create a colormap
cmap = plt.get_cmap("viridis", len(unique_agent_ids))

# Initialize a counter for the color index
color_index = 0

for agent_id in traj["id"].unique():
    agent_data = traj[traj["id"] == agent_id]
    color = cmap(color_index)
    # Move to the next color index
    color_index += 1

    # Position
    axes.plot(
        agent_data["x"],
        agent_data["y"],
        label=f"Head of Agent {agent_id}",
        color=color,
    )
    # head position
    axes.plot(
        agent_data["head_pos_x"], agent_data["head_pos_y"], alpha=0.3, color=color
    )
    # heel right position
    axes.plot(
        agent_data["heel_right_pos_x"],
        agent_data["heel_right_pos_y"],
        alpha=0.3,
        color=color,
    )
    # heel left position
    axes.plot(
        agent_data["heel_left_pos_x"],
        agent_data["heel_left_pos_y"],
        alpha=0.3,
        color=color,
    )

axes.set_xlabel("x/m")
axes.set_ylabel("y/m")
axes.set_aspect("equal")
plt.show()
