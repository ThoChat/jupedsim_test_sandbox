import pathlib
import matplotlib.pyplot as plt
import jupedsim as jps
import pedpy
from numpy.random import normal  # normal distribution of free movement speed
from shapely import Polygon

## Setup geometries
area = Polygon([(0, 0), (12, 0), (12, 12), (10, 12), (10, 2), (0, 2)])
walkable_area = pedpy.WalkableArea(area)
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


## Setup spawning area
spawning_area = Polygon([(0, 0), (6, 0), (6, 2), (0, 2)])
pos_in_spawning_area = jps.distribute_until_filled(
    polygon=spawning_area,
    distance_to_agents=5,
    distance_to_polygon=0.4,
    seed=1,
)
num_agents = len(pos_in_spawning_area)
exit_area = Polygon([(10, 11), (12, 11), (12, 12), (10, 12)])


## Setup Simulation
trajectory_file = "corner_HumanoidModelV0.sqlite"  # output file
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
# v_distribution = normal(5, 0.5, num_agents)

for pos, v0 in zip(pos_in_spawning_area, v_distribution):
    simulation.add_agent(
        jps.HumanoidModelV0AgentParameters(
            journey_id=journey_id,
            stage_id=exit_id,
            position=pos,
            desiredSpeed=v0,
            height=1.75,
        )
    )

# figure, ax = plt.subplots(figsize=(10, 6))
# pedpy.plot_walkable_area(walkable_area=walkable_area, axes=ax).set_aspect("equal")
# # plt.show()

## run simulation
while simulation.agent_count() > 0:
    simulation.iterate()

    # ## plot the trajectory of the agents
    # for agent in simulation.agents():
    #     ax.scatter(
    #         agent.position[0],
    #         agent.position[1],
    #         color="blue",
    #         s=10,
    #         label="Agent Trajectory",
    #     )
    # if simulation.iteration_count() % 100 == 0:
    #     plt.show()
    #     figure, ax = plt.subplots(figsize=(10, 6))
    #     pedpy.plot_walkable_area(walkable_area=walkable_area, axes=ax).set_aspect(
    #         "equal"
    #     )

## Import Sqlite with PedPy
# from sqlite_loader_moded_pepy_fun import *

# TrajectoryData = load_trajectory_from_jupedsim_sqlite(pathlib.Path(trajectory_file))
