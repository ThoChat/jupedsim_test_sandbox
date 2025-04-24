import sqlite3
import difflib


def get_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = sorted(row[0] for row in cursor.fetchall() if row[0])
    conn.close()
    return schema


def get_table_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_data(db_path, table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = sorted(cursor.fetchall())
    conn.close()
    return data


def diff_text(list1, list2, label1="DB1", label2="DB2"):
    diff = difflib.unified_diff(
        list1, list2, fromfile=label1, tofile=label2, lineterm=""
    )
    return "\n".join(diff)


# --- Main logic ---
db1 = "quick_corridor_sim.sqlite"
db2 = "ref_quick_compare.sqlite"

# Compare schemas
schema1 = get_schema(db1)
schema2 = get_schema(db2)
print("🔍 Schema differences:")
print(diff_text(schema1, schema2, "quick_test", "ref_quick_test"))


# to round up floats in tuples
def round_tuple(t, ndigits=6):
    return tuple(round(x, ndigits) if isinstance(x, float) else x for x in t)


# Compare data in tables both DBs share
common_tables = set(get_table_names(db1)) & set(get_table_names(db2))
for table in sorted(common_tables):
    if table == "frame_data" or table == "geometry":
        continue
    data1_raw = get_table_data(db1, table)
    data2_raw = get_table_data(db2, table)

    data1 = [round_tuple(row) for row in data1_raw]
    data2 = [round_tuple(row) for row in data2_raw]
    if data1 != data2:
        print(f"\n Differences in table '{table}':")

        # Use SequenceMatcher to show differences side by side
        matcher = difflib.SequenceMatcher(None, data1, data2)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace":
                for line1, line2 in zip(data1[i1:i2], data2[j1:j2]):
                    print(f"REPLACED:\n  Expected: {line1}\n  Actual:   {line2}")
                    input()
                if (i2 - i1) != (j2 - j1):  # In case of unequal lengths
                    extra_from_1 = data1[i1 + (j2 - j1) : i2]
                    extra_from_2 = data2[j1 + (i2 - i1) : j2]
                    for line in extra_from_1:
                        print(f"REMOVED (extra): {line}")
                        input()
                    for line in extra_from_2:
                        print(f"ADDED (extra):   {line}")
                        input()
            elif tag == "delete":
                for line in data1[i1:i2]:
                    print(f"REMOVED: {line}")
                    input()
            elif tag == "insert":
                for line in data2[j1:j2]:
                    print(f"ADDED:   {line}")
                    input()

print("-- END --")
