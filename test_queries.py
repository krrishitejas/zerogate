import mgclient
from codebase_rag.security_queries import QUERY_BANK

conn = mgclient.connect(host='127.0.0.1', port=7687)
cursor = conn.cursor()

print("Testing direct MATCH (f) RETURN count(f)...")
cursor.execute("MATCH (f) RETURN count(f)")
print(cursor.fetchall())

print("Testing direct source_code is not null...")
try:
    cursor.execute("MATCH (f) WHERE f.source_code IS NOT NULL RETURN f.name")
    print("Nodes with source_code:", cursor.fetchall())
except Exception as e:
    print(e)
    conn.rollback()

for q in QUERY_BANK:
    print(f"Testing {q.id}...")
    try:
        cursor.execute(q.cypher)
        rows = cursor.fetchall()
        print(f"  -> Found {len(rows)} matches")
        for r in rows:
            print(f"     Match: {r}")
    except Exception as e:
        print(f"  -> Error: {e}")
        conn.rollback()

