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
    height = 1.75
    pelvis_width = height * 0.4 / 1.7
    feet_length = height * (0.1470 * 0.75)
    trunk_length = height * 0.3495
    shoulder_width = height * 0.45 / 1.7
    neck_length = height * 0.1396

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
        ax.set_zlim(0, 2)
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
            head_pos = np.array(
                [
                    agent[6],
                    agent[7],
                    agent[8],
                ]
            )
            pelvis_pos = np.array(
                [
                    agent[9],
                    agent[10],
                    agent[11],
                ]
            )
            heel_right_pos = np.array(
                [
                    agent[12],
                    agent[13],
                    agent[14],
                ]
            )

            heel_left_pos = np.array(
                [
                    agent[15],
                    agent[16],
                    agent[17],
                ]
            )

            toe_right_pos = np.array(
                [
                    agent[18],
                    agent[19],
                    agent[20],
                ]
            )
            toe_left_pos = np.array(
                [
                    agent[21],
                    agent[22],
                    agent[23],
                ]
            )

            pelvis_rotation_angle_z = agent[24]
            shoulder_rotation_angle_z = agent[25]
            trunk_rotation_angle_x = agent[26]
            trunk_rotation_angle_y = agent[27]

            # Calculate the end points of the pelvis segment
            pelvis_right_x = pelvis_pos[0] + (
                np.cos(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_right_y = pelvis_pos[1] + (
                np.sin(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_left_x = pelvis_pos[0] - (
                np.cos(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_left_y = pelvis_pos[1] - (
                np.sin(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )

            # Plot the pelvis segment
            ax.plot(
                [pelvis_right_x, pelvis_left_x],
                [pelvis_right_y, pelvis_left_y],
                [pelvis_pos[2], pelvis_pos[2]],
                "b-",
            )

            # Calculate the end points of the right foot
            right_foot_end_x1 = heel_right_pos[0]
            right_foot_end_y1 = heel_right_pos[1]
            right_foot_end_x2 = toe_right_pos[0]
            right_foot_end_y2 = toe_right_pos[1]

            # Plot the right foot
            ax.plot(
                [right_foot_end_x1, right_foot_end_x2],
                [right_foot_end_y1, right_foot_end_y2],
                [heel_right_pos[2], heel_right_pos[2]],
                "g-",
            )

            # Calculate the end points of the left foot
            left_foot_end_x1 = heel_left_pos[0]
            left_foot_end_y1 = heel_left_pos[1]
            left_foot_end_x2 = toe_left_pos[0]
            left_foot_end_y2 = toe_left_pos[1]

            # Plot the left foot
            ax.plot(
                [left_foot_end_x1, left_foot_end_x2],
                [left_foot_end_y1, left_foot_end_y2],
                [heel_left_pos[2], heel_left_pos[2]],
                "r-",
            )

            # Plot the segments linking the pelvis and the feet
            ax.plot(
                [pelvis_right_x, right_foot_end_x1],
                [pelvis_right_y, right_foot_end_y1],
                [pelvis_pos[2], heel_right_pos[2]],
                "b-",
            )
            ax.plot(
                [pelvis_left_x, left_foot_end_x1],
                [pelvis_left_y, left_foot_end_y1],
                [pelvis_pos[2], heel_left_pos[2]],
                "b-",
            )

            # Calculate the position of C7
            c7_pos_x = pos_x + ori_x * np.sin(trunk_rotation_angle_y) * trunk_length
            c7_pos_y = pos_y + (ori_y * np.sin(trunk_rotation_angle_x) * trunk_length)
            c7_pos_z = pelvis_pos[2] + (
                trunk_length
                * np.cos(trunk_rotation_angle_x)
                * np.cos(trunk_rotation_angle_y)
            )

            # Plot the trunk segment
            ax.plot(
                [pos_x, c7_pos_x],
                [pos_y, c7_pos_y],
                [pelvis_pos[2], c7_pos_z],
                "b-",
            )

            # Calculate the head position ### Math have to be checked
            head_pos_x = c7_pos_x
            head_pos_y = c7_pos_y
            head_pos_z = c7_pos_z + neck_length

            # Plot the head position ### Math have to be checked (x,y rotation missing)
            ax.plot(
                [head_pos_x], [head_pos_y], [head_pos_z], "b", marker="o", markersize=1
            )

            # Calculate the shoulder segment
            shoulder_right_x = c7_pos_x + (
                np.cos(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_right_y = c7_pos_y + (
                np.sin(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_left_x = c7_pos_x - (
                np.cos(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_left_y = c7_pos_y - (
                np.sin(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )

            # Plot the shoulder segment
            ax.plot(
                [shoulder_right_x, shoulder_left_x],
                [shoulder_right_y, shoulder_left_y],
                [pelvis_pos[2] + trunk_length, pelvis_pos[2] + trunk_length],
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
