import pathlib
import jupedsim as jps
import pedpy
from shapely import Polygon
from numpy.random import normal

## Setup geometries
area = Polygon([(-5, -5), (5, -5), (5, 5), (-5, 5)])
walkable_area = pedpy.WalkableArea(area)
# pedpy.plot_walkable_area(walkable_area=walkable_area).set_aspect("equal")


starting_positions = [
    (-4, -4),
    (4, -4),
    (4, 4),
    (-4, 4),
]

num_agents = len(starting_positions)  # one agent per starting position

exit_area_list = []
# Define exit mappings: 1st exit → 2nd start, 2nd exit → 1st start, 3rd exit → 4th start, 4th exit → 3rd start
exit_mapping = [
    2,
    3,
    0,
    1,
]  # Index mapping: exit i goes to starting position exit_mapping[i]
for i, pos in enumerate(starting_positions):
    target_pos = starting_positions[exit_mapping[i]]
    x, y = target_pos
    # Create a 1m x 1m square centered at the target starting position
    exit_polygon = Polygon(
        [(x - 0.5, y - 0.5), (x + 0.5, y - 0.5), (x + 0.5, y + 0.5), (x - 0.5, y + 0.5)]
    )
    exit_area_list.append(exit_polygon)


## Setup Simulation
trajectory_file = "four_way_crossing_HumanoidModelV0.sqlite"  # output file
simulation = jps.Simulation(
    model=jps.HumanoidModelV0(),
    geometry=area,
    trajectory_writer=jps.SqliteHumanoidTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

journey_id_list = []
exit_id_list = []
for exit_area in exit_area_list:
    exit_id = simulation.add_exit_stage(exit_area.exterior.coords[:-1])
    journey = jps.JourneyDescription([exit_id])
    exit_id_list.append(exit_id)
    journey_id_list.append(simulation.add_journey(journey))


## Spawn agents
v_distribution = normal(1.34, 0.5, num_agents)


for pos, v0, journey_id, exit_id in zip(
    starting_positions, v_distribution, journey_id_list, exit_id_list
):
    simulation.add_agent(
        jps.HumanoidModelV0AgentParameters(
            journey_id=journey_id,
            stage_id=exit_id,
            position=pos,
            desiredSpeed=v0,
            height=1.75,
        )
    )

while simulation.agent_count() > 0 and simulation.iteration_count() <= 3000:
    if simulation.iteration_count() == 3000:
        print("Simulation stopped after 3000 iterations.")

    simulation.iterate()
