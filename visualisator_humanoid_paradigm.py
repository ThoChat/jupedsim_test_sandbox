import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import sys

# from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


# Connect to the SQLite database
def create_visualisator(simulation_file_name, saving_file_name=""):
    conn = sqlite3.connect(simulation_file_name)
    cursor = conn.cursor()

    # Get the frame data
    cursor.execute("SELECT * FROM trajectory_data ORDER BY frame")
    frame_data = cursor.fetchall()

    # Get the bounding box of the simulation
    query = "SELECT value FROM metadata WHERE key = ?;"
    cursor.execute(query, ("xmin",))
    xmin = float(cursor.fetchone()[0])
    cursor.execute(query, ("xmax",))
    xmax = float(cursor.fetchone()[0])
    cursor.execute(query, ("ymin",))
    ymin = float(cursor.fetchone()[0])
    cursor.execute(query, ("ymax",))
    ymax = float(cursor.fetchone()[0])
    # , xmax, ymin, ymax = cursor.fetchone()

    # Set anthropological parameters
    pelvis_width = 0.4
    pelvis_height = 0.9
    feet_length = 0.25
    trunk_length = 0.7
    shoulder_width = 0.45
    head_length = 0.2

    # Create a 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Initialize the plot view angle
    ax.view_init(elev=45, azim=45)

    def set_plot_view_param():
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_zlim(-pelvis_height, 2)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])

    # Function to update the plot for each frame
    def update(frame):
        ax.clear()
        set_plot_view_param()

        # Get the agent data for the current frame
        agent_data = [row for row in frame_data if row[0] == frame]

        # Plot the pelvis segment and feet for each agent
        for agent in agent_data:
            pos_x, pos_y = agent[2], agent[3]
            ori_x, ori_y = agent[4], agent[5]
            normal_ori_x, normal_ori_y = -ori_y, ori_x
            (
                heel_right_pos_x,
                heel_right_pos_y,
                heel_right_pos_z,
            ) = (
                agent[12],
                agent[13],
                agent[14],
            )
            heel_left_pos_x, heel_left_pos_y, heel_left_pos_z = (
                agent[15],
                agent[16],
                agent[17],
            )
            shoulder_rotation_angle_z = agent[7]
            trunk_rotation_angle_x = agent[10]
            trunk_rotation_angle_y = agent[11]

            # Calculate the end points of the pelvis segment
            pelvis_right_x = pos_x - (normal_ori_x * pelvis_width * 0.5)
            pelvis_right_y = pos_y - (normal_ori_y * pelvis_width * 0.5)
            pelvis_left_x = pos_x + (normal_ori_x * pelvis_width * 0.5)
            pelvis_left_y = pos_y + (normal_ori_y * pelvis_width * 0.5)

            # Plot the pelvis segment
            ax.plot(
                [pelvis_right_x, pelvis_left_x],
                [pelvis_right_y, pelvis_left_y],
                [0, 0],
                "b-",
            )

            # Calculate the end points of the right foot
            right_foot_end_x1 = heel_right_pos_x
            right_foot_end_y1 = heel_right_pos_y
            right_foot_end_x2 = heel_right_pos_x + (ori_x * feet_length)
            right_foot_end_y2 = heel_right_pos_y + (ori_y * feet_length)

            # Plot the right foot
            ax.plot(
                [right_foot_end_x1, right_foot_end_x2],
                [right_foot_end_y1, right_foot_end_y2],
                [heel_right_pos_z - pelvis_height, heel_right_pos_z - pelvis_height],
                "g-",
            )

            # Calculate the end points of the left foot
            left_foot_end_x1 = heel_left_pos_x
            left_foot_end_y1 = heel_left_pos_y
            left_foot_end_x2 = heel_left_pos_x + (ori_x * feet_length)
            left_foot_end_y2 = heel_left_pos_y + (ori_y * feet_length)

            # Plot the left foot
            ax.plot(
                [left_foot_end_x1, left_foot_end_x2],
                [left_foot_end_y1, left_foot_end_y2],
                [heel_left_pos_z - pelvis_height, heel_left_pos_z - pelvis_height],
                "r-",
            )

            # Plot the segments linking the pelvis and the feet
            ax.plot(
                [pelvis_right_x, right_foot_end_x1],
                [pelvis_right_y, right_foot_end_y1],
                [0, -pelvis_height],
                "b-",
            )
            ax.plot(
                [pelvis_left_x, left_foot_end_x1],
                [pelvis_left_y, left_foot_end_y1],
                [0, -pelvis_height],
                "b-",
            )

            # Calculate the position of C7
            c7_pos_x = pos_x + ori_x * np.sin(trunk_rotation_angle_y) * trunk_length
            c7_pos_y = pos_y + (ori_y * np.sin(trunk_rotation_angle_x) * trunk_length)
            c7_pos_z = (
                trunk_length
                * np.cos(trunk_rotation_angle_x)
                * np.cos(trunk_rotation_angle_y)
            )

            # Plot the trunk segment
            ax.plot(
                [pos_x, c7_pos_x],
                [pos_y, c7_pos_y],
                [0, c7_pos_z],
                "b-",
            )

            # Calculate the head position ### Math have to be checked
            head_pos_x = c7_pos_x
            head_pos_y = c7_pos_y
            head_pos_z = c7_pos_z + head_length

            # Plot the head position ### Math have to be checked (x,y rotation missing)
            ax.plot(
                [head_pos_x], [head_pos_y], [head_pos_z], "b", marker="o", markersize=1
            )

            # Calculate the shoulder segment
            shoulder_right_x = c7_pos_x - (
                np.cos(shoulder_rotation_angle_z) * normal_ori_x * shoulder_width * 0.5
            )
            shoulder_right_y = c7_pos_y - (
                np.sin(shoulder_rotation_angle_z) * normal_ori_y * shoulder_width * 0.5
            )
            shoulder_left_x = c7_pos_x + (
                np.cos(shoulder_rotation_angle_z) * normal_ori_x * shoulder_width * 0.5
            )
            shoulder_left_y = c7_pos_y + (
                np.sin(shoulder_rotation_angle_z) * normal_ori_y * shoulder_width * 0.5
            )

            # Plot the shoulder segment
            ax.plot(
                [shoulder_right_x, shoulder_left_x],
                [shoulder_right_y, shoulder_left_y],
                [trunk_length, trunk_length],
                "b-",
            )

    # Create the animation
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=range(1, max(frame_data, key=lambda x: x[0])[0] + 1),
        interval=25,
    )

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=range(1, max(frame_data, key=lambda x: x[0])[0] + 1),
        interval=25,
    )

    if saving_file_name != "":
        # Save the animation as a video file
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist="Me"))
        anim.save(saving_file_name, writer=writer)
    else:
        plt.show()


if __name__ == "__main__":
    file_name = sys.argv[1]
    saving_file_name = sys.argv[2] if len(sys.argv) > 2 else ""
    create_visualisator(file_name, saving_file_name)
