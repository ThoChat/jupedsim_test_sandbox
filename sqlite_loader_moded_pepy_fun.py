"""Load trajectories to the internal trajectory data format."""

import math
import pathlib
import sqlite3
from enum import Enum
from typing import Any, Optional, Tuple

import h5py  # type: ignore
import pandas as pd
import shapely

from pedpy.column_identifier import FRAME_COL, ID_COL, X_COL, Y_COL
from pedpy.data.geometry import WalkableArea
from pedpy.data.trajectory_data import TrajectoryData


class LoadTrajectoryError(Exception):
    """Class reflecting errors when loading trajectories with PedPy."""

    def __init__(self, message):
        """Create LoadTrajectoryError with the given message.

        Args:
            message: Error message
        """
        self.message = message


def _validate_is_file(file: pathlib.Path) -> None:
    """Validates if the given file is a valid file, if valid raises Exception.

    A file is considered invalid if:

    - it does not exist
    - is not a file, but a directory

    Args:
        file: File to check


    """
    if not file.exists():
        raise LoadTrajectoryError(f"{file} does not exist.")

    if not file.is_file():
        raise LoadTrajectoryError(f"{file} is not a file.")


def load_trajectory_from_jupedsim_sqlite(
    trajectory_file: pathlib.Path,
) -> TrajectoryData:
    """Loads data from the sqlite file as :class:`~trajectory_data.TrajectoryData`.

    Args:
        trajectory_file: trajectory file in JuPedSim sqlite format

    Returns:
        TrajectoryData: :class:`~trajectory_data.TrajectoryData` representation of the file data
    """
    _validate_is_file(trajectory_file)

    with sqlite3.connect(trajectory_file) as con:
        try:
            data = pd.read_sql_query(
                "select frame, id,"
                + "pos_x as x, pos_y as y,"
                + "head_pos_x, head_pos_y,"
                + "shoulder_rotation_angle_z, "
                + "trunk_rotation_angle_x, "
                + "trunk_rotation_angle_y, "
                + "heel_right_pos_x, heel_right_pos_y,"
                + "heel_left_pos_x, heel_left_pos_y from trajectory_data",
                con,
            )
        except Exception as exc:
            raise LoadTrajectoryError(
                "The given sqlite trajectory is not a valid JuPedSim format, it does not not "
                "contain a 'trajectory_data' table. Please check your file."
            ) from exc
        if data.empty:
            raise LoadTrajectoryError(
                "The given sqlite trajectory file seems to be empty. "
                "Please check your file."
            )

        try:
            fps_query_result = (
                con.cursor()
                .execute("select value from metadata where key = 'fps'")
                .fetchone()
            )
        except Exception as exc:
            raise LoadTrajectoryError(
                "The given sqlite trajectory is not a valid JuPedSim format, it does not not "
                "contain a 'metadata' table. Please check your file."
            ) from exc

        if fps_query_result is None:
            raise LoadTrajectoryError(
                "The given sqlite trajectory file seems not include a frame rate. "
                "Please check your file."
            )
        fps = float(fps_query_result[0])

    return TrajectoryData(data=data, frame_rate=fps)


def load_walkable_area_from_jupedsim_sqlite(
    trajectory_file: pathlib.Path,
) -> WalkableArea:
    """Loads the walkable area from the sqlite file as :class:`~geometry.WalkableArea`.

    .. note::

        When using a JuPedSim sqlite trajectory file with version 2, the walkable area is the union
        of all provided walkable areas in the file.

    Args:
        trajectory_file: trajectory file in JuPedSim sqlite format

    Returns:
        WalkableArea: :class:`~geometry.WalkableArea` used in the simulation
    """
    _validate_is_file(trajectory_file)

    with sqlite3.connect(trajectory_file) as connection:
        db_version = _get_jupedsim_sqlite_version(connection)

        if db_version == 1:
            return _load_walkable_area_from_jupedsim_sqlite_v1(connection)

        if db_version == 2:
            return _load_walkable_area_from_jupedsim_sqlite_v2(connection)

        raise LoadTrajectoryError(
            f"The given sqlite trajectory has unsupported db version {db_version}. "
            f"Supported are versions: 1, 2."
        )


def _get_jupedsim_sqlite_version(connection: sqlite3.Connection) -> int:
    cur = connection.cursor()
    return int(
        cur.execute(
            "SELECT value FROM metadata WHERE key = ?", ("version",)
        ).fetchone()[0]
    )


def _load_walkable_area_from_jupedsim_sqlite_v1(
    con: sqlite3.Connection,
) -> WalkableArea:
    try:
        walkable_query_result = (
            con.cursor().execute("select wkt from geometry").fetchone()
        )
    except Exception as exc:
        raise LoadTrajectoryError(
            "The given sqlite trajectory is not a valid JuPedSim format, it does not not "
            "contain a 'geometry' table. Please check your file."
        ) from exc

    if walkable_query_result is None:
        raise LoadTrajectoryError(
            "The given sqlite trajectory file seems not include a geometry. "
            "Please check your file."
        )

    return WalkableArea(walkable_query_result[0])


def _load_walkable_area_from_jupedsim_sqlite_v2(
    con: sqlite3.Connection,
) -> WalkableArea:
    try:
        res = con.cursor().execute("SELECT wkt FROM geometry")
        geometries = [shapely.from_wkt(s) for s in res.fetchall()]
    except Exception as exc:
        raise LoadTrajectoryError(
            "The given sqlite trajectory is not a valid JuPedSim format, it does not not "
            "contain a 'geometry' table. Please check your file."
        ) from exc

    if not geometries:
        raise LoadTrajectoryError(
            "The given sqlite trajectory file seems not include a geometry. "
            "Please check your file."
        )

    return WalkableArea(shapely.union_all(geometries))
