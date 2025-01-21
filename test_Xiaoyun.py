import pathlib
import matplotlib.pyplot as plt
import jupedsim as jps
import pedpy
from numpy.random import normal
from shapely import Polygon


area = Polygon([(0, 0), (12, 0), (12, 12), (10, 12), (10, 2), (0, 2)])
walkable_area = pedpy.WalkableArea(area)
pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


spawning_area = Polygon([(0, 0), (6, 0), (6, 2), (0, 2)])
num_agents = 20
pos_in_spawning_area = jps.distributions.distribute_by_number(
    polygon=spawning_area,
    number_of_agents=num_agents,
    distance_to_agents=0.4,
    distance_to_polygon=0.2,
    seed=1,
)
exit_area = Polygon([(10, 11), (12, 11), (12, 12), (10, 12)])


## Setting up the Simulation and Routing Details
trajectory_file = "test_Xiaoyun_corner.sqlite"  # output file
simulation = jps.Simulation(
    model=jps.CollisionFreeSpeedModel(),
    geometry=area,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

exit_id = simulation.add_exit_stage(exit_area.exterior.coords[:-1])
journey = jps.JourneyDescription([exit_id])
journey_id = simulation.add_journey(journey)

v_distribution = normal(1.34, 0.05, num_agents)

for pos, v0 in zip(pos_in_spawning_area, v_distribution):
    simulation.add_agent(
        jps.CollisionFreeSpeedModelAgentParameters(
            journey_id=journey_id, stage_id=exit_id, position=pos, v0=v0
        )
    )


## running the simulation
while simulation.agent_count() > 0:
    simulation.iterate()


## Plotting results
axes = pedpy.plot_walkable_area(walkable_area=walkable_area)
axes.fill(*spawning_area.exterior.xy, color="lightgrey")
axes.fill(*exit_area.exterior.xy, color="indianred")


## Import Sqlite with PedPy
from sqlite_loader_moded_pepy_fun import *

TrajectoryData = load_trajectory_from_jupedsim_sqlite(
    pathlib.Path("../" + trajectory_file)
)
traj = TrajectoryData.data


# Get unique agent IDs
unique_agent_ids = traj["id"].unique()

# Create a colormap
cmap = plt.cm.get_cmap("viridis", len(unique_agent_ids))

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
        agent_data["y"],  # ["head_pos_y"],
        label=f"Head of Agent {agent_id}",
        color=color,
    )
    # head position
    axes.plot(
        agent_data["head_pos_x"], agent_data["head_pos_y"], alpha=0.3, color=color
    )


axes.set_xlabel("x/m")
axes.set_ylabel("y/m")
axes.set_aspect("equal")
plt.show()
