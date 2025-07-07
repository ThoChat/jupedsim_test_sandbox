import sqlite3
import pandas as pd
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from sqlite_loader_moded_pepy_fun import *

simulation_file_name = "corridor_HumanoidModelV0.sqlite"


def load_trajectory_to_dataframe(sqlite_file_path: str) -> pd.DataFrame:
    """
    Load trajectory data from a JuPedSim SQLite file into a Pandas DataFrame.

    Args:
        sqlite_file_path: Path to the SQLite file.

    Returns:
        Pandas DataFrame containing the trajectory data.
    """
    file_path = Path(sqlite_file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Connect to the SQLite database
        with sqlite3.connect(str(file_path)) as conn:
            # Check if the 'trajectory_data' table exists
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='trajectory_data'"
            )
            if not cur.fetchone():
                raise ValueError(
                    "The SQLite file does not contain a 'trajectory_data' table."
                )

            # Query the trajectory data
            query = """
                SELECT 
                    frame, id, 
                    pos_x AS x, pos_y AS y,
                    head_pos_x, head_pos_y, head_pos_z,
                    pelvis_pos_x, pelvis_pos_y, pelvis_pos_z,
                    shoulder_rotation_angle_z,
                    trunk_rotation_angle_x, trunk_rotation_angle_y,
                    heel_right_pos_x, heel_right_pos_y, heel_right_pos_z,
                    heel_left_pos_x, heel_left_pos_y, heel_left_pos_z
                FROM trajectory_data
            """
            df = pd.read_sql_query(query, conn)

        return df

    except sqlite3.Error as e:
        raise RuntimeError(f"SQLite error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error loading SQLite file: {e}") from e


df = load_trajectory_to_dataframe(simulation_file_name)


# Plot the 'heel_left_pos_z' column over the 'frame' column
plt.figure(figsize=(10, 6))
plt.plot(df["frame"], df["pelvis_pos_z"], color="blue")

# Add labels and title
plt.title("Z position of Left Heel Over Time")
plt.xlabel("Frame")
plt.ylabel("Z position")
plt.grid(True)

# Show the plot
plt.show()
