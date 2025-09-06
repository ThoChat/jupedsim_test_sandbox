import sqlite3
from shapely import wkt
import matplotlib.pyplot as plt

# open your database
con = sqlite3.connect("single_indiv_btlnk_HumanoidModelV0.sqlite")
cur = con.cursor()

# get all stored geometries
cur.execute("SELECT wkt FROM geometry")
rows = cur.fetchall()

geometries = [wkt.loads(r[0]) for r in rows]

# Plot all geometries
fig, ax = plt.subplots(figsize=(10, 10))
for geom in geometries:
    print(geom)
    if geom.geom_type == "Polygon":
        # Plot exterior ring
        x, y = geom.exterior.xy
        ax.plot(x, y, color="blue", linewidth=2)

        # Plot interior rings (holes)
        for interior in geom.interiors:
            x, y = interior.xy
            ax.plot(x, y, color="black", linewidth=1)
    elif geom.geom_type == "LineString":
        x, y = geom.xy
        ax.plot(x, y, color="blue", linewidth=2)
    elif geom.geom_type == "Point":
        ax.plot(geom.x, geom.y, "ro", markersize=5)

ax.set_aspect("equal")
plt.title("Geometries from corridor_HumanoidModelV0.sqlite")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.show()

# Close the database connection
con.close()
