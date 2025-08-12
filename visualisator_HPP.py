import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
import sys


def create_visualisator(simulation_file_name, saving_file_name=""):
    conn = sqlite3.connect(simulation_file_name)
    cursor = conn.cursor()

    # Get the frame data
    cursor.execute("SELECT * FROM trajectory_data ORDER BY frame")
    frame_data = cursor.fetchall()

    # Get bounding box
    def get_meta(key):
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        return float(cursor.fetchone()[0])

    xmin = get_meta("xmin")
    xmax = get_meta("xmax")
    ymin = get_meta("ymin")
    ymax = get_meta("ymax")

    # Anthropometric constants
    height = 1.75
    pelvis_width = height * 0.3 / 1.7
    feet_length = height * (0.1470 * 0.75)
    trunk_length = height * 0.3495
    shoulder_width = height * 0.45 / 1.7
    neck_length = height * 0.1396

    max_frame = max(frame_data, key=lambda x: x[0])[0]

    # Figure + axes
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=45, azim=45)

    # Play/Pause button
    ax_play = plt.axes([0.8, 0.025, 0.1, 0.04])
    button_play = Button(ax_play, "Play")
    is_playing = False

    # Slider
    ax_slider = plt.axes([0.2, 0.1, 0.55, 0.03])
    slider = Slider(ax_slider, "Frame", 1, max_frame, valinit=1, valfmt="%0.0f")

    # Set view params
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

    # Plot function
    def plot_frame(frame):
        ax.cla()
        set_plot_view_param()

        # All agents in this frame
        agent_data = [row for row in frame_data if row[0] == frame]

        for agent in agent_data:
            pos_x, pos_y = agent[2], agent[3]
            ori_x, ori_y = agent[4], agent[5]
            pelvis_pos = np.array(agent[9:12])
            heel_right_pos = np.array(agent[12:15])
            heel_left_pos = np.array(agent[15:18])
            toe_right_pos = np.array(agent[18:21])
            toe_left_pos = np.array(agent[21:24])

            pelvis_rotation_angle_z = agent[24]
            shoulder_rotation_angle_z = agent[25]
            trunk_rotation_angle_x = agent[26]
            trunk_rotation_angle_y = agent[27]

            # Pelvis segment
            pelvis_right_x = (
                pelvis_pos[0] + np.cos(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_right_y = (
                pelvis_pos[1] + np.sin(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_left_x = (
                pelvis_pos[0] - np.cos(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )
            pelvis_left_y = (
                pelvis_pos[1] - np.sin(pelvis_rotation_angle_z) * pelvis_width * 0.5
            )

            ax.plot(
                [pelvis_right_x, pelvis_left_x],
                [pelvis_right_y, pelvis_left_y],
                [pelvis_pos[2], pelvis_pos[2]],
                "b-",
            )

            # Feet
            ax.plot(
                [heel_right_pos[0], toe_right_pos[0]],
                [heel_right_pos[1], toe_right_pos[1]],
                [heel_right_pos[2], heel_right_pos[2]],
                "g-",
            )
            ax.plot(
                [heel_left_pos[0], toe_left_pos[0]],
                [heel_left_pos[1], toe_left_pos[1]],
                [heel_left_pos[2], heel_left_pos[2]],
                "r-",
            )

            # Legs
            ax.plot(
                [pelvis_right_x, heel_right_pos[0]],
                [pelvis_right_y, heel_right_pos[1]],
                [pelvis_pos[2], heel_right_pos[2]],
                "b-",
            )
            ax.plot(
                [pelvis_left_x, heel_left_pos[0]],
                [pelvis_left_y, heel_left_pos[1]],
                [pelvis_pos[2], heel_left_pos[2]],
                "b-",
            )

            # C7 position
            c7_pos_x = pos_x + ori_x * np.sin(trunk_rotation_angle_y) * trunk_length
            c7_pos_y = pos_y + ori_y * np.sin(trunk_rotation_angle_x) * trunk_length
            c7_pos_z = pelvis_pos[2] + trunk_length * np.cos(
                trunk_rotation_angle_x
            ) * np.cos(trunk_rotation_angle_y)

            ax.plot(
                [pos_x, c7_pos_x], [pos_y, c7_pos_y], [pelvis_pos[2], c7_pos_z], "b-"
            )

            # Head
            head_pos_x = c7_pos_x
            head_pos_y = c7_pos_y
            head_pos_z = c7_pos_z + neck_length
            ax.plot([head_pos_x], [head_pos_y], [head_pos_z], "bo", markersize=2)

            # Shoulders
            shoulder_right_x = (
                c7_pos_x + np.cos(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_right_y = (
                c7_pos_y + np.sin(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_left_x = (
                c7_pos_x - np.cos(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )
            shoulder_left_y = (
                c7_pos_y - np.sin(shoulder_rotation_angle_z) * shoulder_width * 0.5
            )

            ax.plot(
                [shoulder_right_x, shoulder_left_x],
                [shoulder_right_y, shoulder_left_y],
                [pelvis_pos[2] + trunk_length, pelvis_pos[2] + trunk_length],
                "b-",
            )

        ax.set_title(f"Frame {frame}")

    # Slider update callback
    def slider_update(val):
        frame = int(slider.val)
        plot_frame(frame)
        fig.canvas.draw_idle()

    slider.on_changed(slider_update)

    # Animate callback
    def animate(i):
        nonlocal is_playing
        if is_playing:
            current_frame = int(slider.val)
            next_frame = (current_frame + 1) if current_frame < max_frame else 1
            slider.set_val(next_frame)

    # Button callback
    def toggle_play(event):
        nonlocal is_playing
        is_playing = not is_playing
        button_play.label.set_text("Pause" if is_playing else "Play")

    button_play.on_clicked(toggle_play)

    # Initialize plot
    plot_frame(1)

    # Animation loop
    ani = animation.FuncAnimation(
        fig, animate, frames=max_frame, interval=50, cache_frame_data=False
    )

    if saving_file_name != "":
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist="Me"))
        ani.save(saving_file_name, writer=writer)
    else:
        plt.show()


if __name__ == "__main__":
    file_name = sys.argv[1]
    saving_file_name = sys.argv[2] if len(sys.argv) > 2 else ""
    create_visualisator(file_name, saving_file_name)
