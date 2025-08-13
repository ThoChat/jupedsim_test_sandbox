import jupedsim as jps
import shapely.geometry
import pathlib
import numpy as np

# --- 1. Define the Corridor Geometry ---
# Create a very large, narrow rectangular corridor.
# Example: 10 units long, 10 units wide.
# Coordinates are (x, y) tuples.
corridor_coords = [
    (-10.0, -10),
    (10.0, -10),
    (10.0, 10.0),
    (-10, 10.0),
    (-10, -10),  # Close the polygon
]
polygon = shapely.geometry.Polygon(corridor_coords)

# --- 2. Initialize the Simulation ---

trajectory_file = "arc_circle_HumanoidModelV0.sqlite"  # output file
sim = jps.Simulation(
    model=jps.HumanoidModelV0(),
    geometry=polygon,
    trajectory_writer=jps.SqliteHumanoidTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)
print("Simulation initialized with a large corridor geometry.")

# --- 3. Define Waypoint Stages for arc-circle ---
num_points = 8
angles = np.linspace(0.3, 2 * np.pi, num_points)  # Angles from 0 to pi (half circle)
waypoint_coordinates_x = [5 * np.cos(theta) for theta in angles]
waypoint_coordinates_y = [5 * np.sin(theta) for theta in angles]

waypoint_positions = [
    (x, y) for x, y in zip(waypoint_coordinates_x, waypoint_coordinates_y)
]

# # --- 4. Plot the corridor and the waypoints ---
# import matplotlib.pyplot as plt

# # Plot corridor
# fig, ax = plt.subplots()
# x, y = polygon.exterior.xy
# ax.plot(x, y, "k-", label="Corridor")

# # Plot waypoints
# waypoint_x = [p[0] for p in waypoint_positions]
# waypoint_y = [p[1] for p in waypoint_positions]
# ax.plot(waypoint_x, waypoint_y, "ro", label="Waypoints")

# ax.set_aspect("equal")
# ax.set_title("Corridor and Waypoints")
# ax.legend()
# plt.show()

waypoint_ids = []
waypoint_reach_distance = 0.25  # The distance within which an agent is considered to have reached the waypoint

for i, pos in enumerate(waypoint_positions):
    # Add each waypoint stage to the simulation.
    stage_id = sim.add_waypoint_stage(position=pos, distance=waypoint_reach_distance)
    waypoint_ids.append(stage_id)
    print(f"Added Waypoint Stage {i+1} at {pos} with ID: {stage_id}")

# --- 4. Define the Exit Stage ---
exit = [
    (9.8, 0.0),
    (10.0, 0.0),
    (10.0, 0.2),
    (9.8, 0.2),
    (9.8, 0.0),  # Close the polygon
]
exit_polygon = shapely.geometry.Polygon(exit)
# Add the exit stage to the simulation. [8]
exit_stage_id = sim.add_exit_stage(polygon=exit_polygon)

print(f"Added Exit Stage at {exit} with ID: {exit_stage_id}")

# --- 5. Define the Agent's Journey (Zig-Zag Path) ---
# A Journey describes the sequence of stages an agent should take. [5, 16]
journey = jps.JourneyDescription()

# Add stages to the journey and set transitions.
# The agent will follow a fixed path: WP1 -> WP2 -> WP3 -> WP4 -> WP5 -> Exit. [18]
for i in range(len(waypoint_ids) - 1):
    current_wp_id = waypoint_ids[i]
    next_wp_id = waypoint_ids[i + 1]
    journey.add(current_wp_id)  # Add the current waypoint to the journey. [16]
    # Set a fixed transition from the current waypoint to the next. [19]
    fixed_transition = jps.Transition.create_fixed_transition(next_wp_id)
    journey.set_transition_for_stage(current_wp_id, fixed_transition)  # [6, 16]
    print(
        f"Journey: Set fixed transition from Waypoint {current_wp_id} to Waypoint {next_wp_id}"
    )

# Set the transition from the last waypoint to the exit stage.
last_wp_id = waypoint_ids[-1]
journey.add(last_wp_id)  # Add the last waypoint to the journey. [16]
fixed_transition_to_exit = jps.Transition.create_fixed_transition(exit_stage_id)  # [19]
journey.set_transition_for_stage(last_wp_id, fixed_transition_to_exit)  # [6, 16]
print(
    f"Journey: Set fixed transition from last Waypoint {last_wp_id} to Exit {exit_stage_id}"
)

# Optionally, add the exit stage to the journey as its final destination. [16]
journey.add(exit_stage_id)

# Add the defined journey to the simulation. [27]
journey_id = sim.add_journey(journey)
print(f"Added Journey with ID: {journey_id}")

# --- 6. Add the Single Agent ---
# Define the initial parameters for the agent.
agent_start_position = waypoint_positions
agent_parameters = jps.HumanoidModelV0AgentParameters(
    journey_id=journey_id,  # Assign the agent to the zig-zag journey. [29]
    stage_id=1,  # Agent initially targets the first waypoint. [29]
    position=(1.0, 1.0),  # Initial position of the agent. [28]
    desiredSpeed=5,
    height=1.75,
)

# Add the agent to the simulation. [2]
agent_id = sim.add_agent(agent_parameters)
print(
    f"Added single Agent with ID: {agent_id} at {agent_start_position}, targeting Waypoint {waypoint_ids}"
)

# --- 7. Run the Simulation ---
max_iterations = 5000  # Set a maximum number of iterations to prevent infinite loops.

print("\nStarting simulation loop...")
for i in range(max_iterations):
    sim.iterate()  # Advance the simulation by one iteration. [3, 30]

    # Check if the agent has been removed (e.g., by reaching an exit stage). [31]
    if agent_id in sim.removed_agents():
        print(
            f"Agent {agent_id} successfully exited the simulation at iteration {sim.iteration_count()}."
        )
        break

    # Optional: Print agent's current state periodically for monitoring.
    if i % 100 == 0:
        try:
            current_agent = sim.agent(
                agent_id
            )  # Access specific agent in the simulation. [32]
            print(
                f"Iteration {sim.iteration_count()}: Agent {agent_id} Position: {current_agent.position}, Targeting Stage ID: {current_agent.stage_id}, Journey ID: {current_agent.journey_id}"
            )  # [33, 34]
        except (
            Exception
        ):  # Agent might have been removed in a non-exit way (e.g., error)
            print(
                f"Agent {agent_id} no longer exists in simulation after iteration {sim.iteration_count()}."
            )
            break

print(f"\nSimulation finished. Total iterations: {sim.iteration_count()}.")
