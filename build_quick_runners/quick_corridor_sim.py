###########################################################
####   This sript create a simple corridor simulation #####
###########################################################

import numpy as np
import pathlib
import matplotlib.pyplot as plt
import jupedsim as jps
import pedpy
from shapely import Polygon

## Setup geometries
area = Polygon([(0, 0), (2, 0), (2, 10), (0, 10)])
walkable_area = pedpy.WalkableArea(area)
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


## Setup spawning area
spawning_area = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
pos_in_spawning_area = [
    (0.834044009405148, 1.4406489868843162),
    (np.float64(0.35818596216566845), np.float64(0.3368317073802509)),
    (np.float64(1.3621137797930702), np.float64(0.5038329238188515)),
]
# pos_in_spawning_area = jps.distribute_until_filled(
#     polygon=spawning_area,
#     distance_to_agents=0.8,
#     distance_to_polygon=0.3,
#     seed=1,
# )
num_agents = len(pos_in_spawning_area)
exit_area = Polygon([(0, 9), (2, 9), (2, 10), (0, 10)])


## Setup Simulation
trajectory_file = "quick_corridor_sim.sqlite"  # output file
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
v_distribution = np.ones(num_agents)

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
