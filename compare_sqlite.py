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
db1 = "quick_test.sqlite"
db2 = "ref_quick_test.sqlite"

# Compare schemas
schema1 = get_schema(db1)
schema2 = get_schema(db2)
print("🔍 Schema differences:")
print(diff_text(schema1, schema2, "quick_test", "ref_quick_test"))

# Compare data in tables both DBs share
common_tables = set(get_table_names(db1)) & set(get_table_names(db2))
for table in sorted(common_tables):
    if table == "frame_data" or table == "geometry":
        continue
    data1 = [str(row) for row in get_table_data(db1, table)]
    data2 = [str(row) for row in get_table_data(db2, table)]
    if data1 != data2:
        print(f"\n🔍 Differences in table '{table}':")
        print(
            diff_text(data1, data2, f"{table} @quick_test", f"{table}@ref_quick_test")
        )
print("-- END --")
