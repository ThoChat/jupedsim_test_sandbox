import pathlib
import jupedsim as jps
import pedpy
import numpy as np
from numpy.random import normal  # normal distribution of free movement speed
from shapely import Polygon

## Setup geometries
# area = Polygon([(0, 0), (2, 0), (2, 20), (0, 20)])  # corridor along y-axis

area = Polygon([(0, 0), (20, 0), (20, 5), (0, 5)])  # corridor along x-axis

walkable_area = pedpy.WalkableArea(area)
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


## Setup spawning area
# spawning_area = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])  # for corridor along y-axis
spawning_area = Polygon(
    [(0.5, 0.5), (4.5, 0.5), (4.5, 4.5), (0, 4.5)]
)  # for corridor along x-axis
num_agents = 1
pos_in_spawning_area = jps.distributions.distribute_by_number(
    polygon=spawning_area,
    number_of_agents=num_agents,
    distance_to_agents=0.6,
    distance_to_polygon=0.15,
    seed=1,
)
num_agents = len(pos_in_spawning_area)
# exit_area = Polygon([(0, 9), (2, 9), (2, 20), (0, 20)])  # for corridor along y-axis
exit_area = Polygon([(18, 0), (20, 0), (20, 5), (18, 5)])  # for corridor along x-axis


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
v_distribution = normal(1.5, 0.2, num_agents)
# v_distribution = normal(6, 0.05, num_agents)

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
while simulation.agent_count() > 0 and simulation.iteration_count() <= 3000:
    if simulation.iteration_count() == 3000:
        print("Simulation stopped after 3000 iterations.")

    # # introduice a perturbation of the XCoM
    # if simulation.iteration_count() == 250:
    #     current_agent = simulation.agent(agent_id)
    #     current_agent.model.Xcom = tuple(
    #         np.array(current_agent.model.Xcom) + np.array([0.0, 0.0])
    #     )

    simulation.iterate()


## Import Sqlite with PedPy
from sqlite_loader_moded_pepy_fun import *

TrajectoryData = load_trajectory_from_jupedsim_sqlite(pathlib.Path(trajectory_file))
traj = TrajectoryData.data
