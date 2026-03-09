import mgclient
conn = mgclient.connect(host='127.0.0.1', port=7687)
cursor = conn.cursor()
cursor.execute("MATCH (n:Function) RETURN n.name, substring(n.source_code, 0, 80)")
functions = cursor.fetchall()
print(f"Found {len(functions)} functions:")
for row in functions:
    print(f"  {row[0]}: {row[1]}")

cursor.execute("MATCH (n:File) RETURN n.name, substring(n.source_code, 0, 80)")
files = cursor.fetchall()
print(f"\nFound {len(files)} files:")
for row in files:
    print(f"  {row[0]}: {row[1]}")
