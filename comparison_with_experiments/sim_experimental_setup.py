# 040_l020_g1_rf_h-: POLYGON ((5 -5, 5 2, -5 2, -5 -5, 5 -5), (0.2 0, 3.2 0, 3.2 1, 1 1, 1 0.2, 0.2 0.2, 0.2 0), (-0.2 0, -0.2 0.2, -1 0.2, -1 1, -3.2 1, -3.2 0, -0.2 0))

import pathlib
import jupedsim as jps
import pedpy
from numpy.random import normal  # normal distribution of free movement speed
from shapely import Polygon
from shapely.wkt import loads
import matplotlib.pyplot as plt
import numpy as np


## Setup geometries
bottleneck_width = 0.4
area_exp = loads(
    f"POLYGON ((5 -5, 5 2, -5 2, -5 -5, 5 -5), "
    f"({bottleneck_width} 0, 4.99 0, 4.99 1, 1 1, 1 {bottleneck_width}, {bottleneck_width} {bottleneck_width}, {bottleneck_width} 0), "
    f"(-{bottleneck_width} 0, -{bottleneck_width} {bottleneck_width}, -1 {bottleneck_width}, -1 1, -4.99 1, -4.99 0, -{bottleneck_width} 0))"
)


### to visualize trajectories ###
# walkable_area = pedpy.WalkableArea(area_exp)
# file = pathlib.Path(
#     "./../../../Juelich_database/bottleneck_single_individuals/trajectories_hdf5/040_l020_g1_rf_h-.h5"
# )

# trajectory = pedpy.load_trajectory_from_ped_data_archive_hdf5(trajectory_file=file)

# pedpy.plot_trajectories(traj=trajectory, walkable_area=walkable_area).set_aspect(
#     "equal"
# )
# plt.show()
##################################


## all starting positions (for left to right when looking to the bottleneck)
starting_positions = [
    # (-4, -0.5),
    (-3.7, -2.15),
    (-2.15, -3.7),
    (0, -4),
    (2.15, -3.7),
    (3.7, -2.15),
    (4, -0.5),
]

num_agents = len(starting_positions)  # one agent per starting position

exit_area = Polygon([(-0.5, 1.0), (0.5, 1.0), (0.5, 1.3), (-0.5, 1.3)])


## Setup Simulation
trajectory_file = "single_indiv_btlnk_HumanoidModelV0.sqlite"  # output file
simulation = jps.Simulation(
    model=jps.HumanoidModelV0(),
    geometry=area_exp,
    trajectory_writer=jps.SqliteHumanoidTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

exit_id = simulation.add_exit_stage(exit_area.exterior.coords[:-1])
journey = jps.JourneyDescription([exit_id])
journey_id = simulation.add_journey(journey)

## Spawn agents
v_distribution = normal(1.34, 0.5, num_agents)

## Add the first agent with a fixed position
simulation.add_agent(
    jps.HumanoidModelV0AgentParameters(
        journey_id=journey_id,
        stage_id=exit_id,
        position=starting_positions[0],
        desiredSpeed=v_distribution[0],
        height=1.75,
        radius=0.05,
    )
)

figure, ax = plt.subplots(figsize=(10, 6))
pedpy.plot_walkable_area(walkable_area=pedpy.WalkableArea(area_exp), ax=ax).set_aspect(
    "equal"
)

## run simulation
# print(isinstance(agent.model, jps.py_jupedsim.HumanoidModelV0State))
while simulation.agent_count() > 0 and simulation.iteration_count() < 3000:

    simulation.iterate()
