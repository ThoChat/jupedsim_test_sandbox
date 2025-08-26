import pathlib
import jupedsim as jps
import pedpy
import numpy as np
from numpy.random import normal  # normal distribution of free movement speed
from shapely import Polygon, GeometryCollection

## Setup geometries
room1 = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
room2 = Polygon([(15, 0), (25, 0), (25, 10), (15, 10)])
corridor = Polygon([(10, 4.5), (28, 4.5), (28, 5.5), (10, 5.5)])

area = GeometryCollection(corridor.union(room1.union(room2)))
walkable_area = pedpy.WalkableArea(area.geoms[0])
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")

## Setup spawning area
spawning_area = Polygon([(0.3, 0.3), (5, 0.3), (5, 9.7), (0.3, 9.7)])
num_agents = 1
pos_in_spawning_area = jps.distributions.distribute_by_number(
    polygon=spawning_area,
    number_of_agents=num_agents,
    distance_to_agents=0.3,
    distance_to_polygon=0.15,
    seed=1,
)
exit_area = Polygon([(27, 4.5), (28, 4.5), (28, 5.5), (27, 5.5)])


## Setup Simulation
trajectory_file = "bottleneck_HumanoidModelV0.sqlite"  # output file
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
# v_distribution = normal(10, 0.5, num_agents)

for pos, v0 in zip(pos_in_spawning_area, v_distribution):
    agent_id = simulation.add_agent(
        jps.HumanoidModelV0AgentParameters(
            journey_id=journey_id,
            stage_id=exit_id,
            position=pos,
            desiredSpeed=v0,
            height=1.75,
        )
    )

## run simulation
while simulation.agent_count() > 0 and simulation.iteration_count() <= 5000:

    simulation.iterate()
    if simulation.iteration_count() == 5000:
        print("Simulation stopped after 5000 iterations.")


## Import Sqlite with PedPy
# from sqlite_loader_moded_pepy_fun import *

# TrajectoryData = load_trajectory_from_jupedsim_sqlite(pathlib.Path(trajectory_file))
# traj = TrajectoryData.data
