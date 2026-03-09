import mgclient
import time

def test(name, q):
    print(f"Testing: {name}")
    print(f"Query: {q.strip()}")
    try:
        conn = mgclient.connect(host='127.0.0.1', port=7687)
        cursor = conn.cursor()
        cursor.execute(q)
        print(" -> Success! Matches:", len(cursor.fetchall()))
    except Exception as e:
        print(" -> Error:", e)

print("Testing simple RegExp...")
test("Double Backslash Dot", r"""MATCH (f:Function) WHERE f.source_code =~ ".*foo\\..*" RETURN count(f)""")

test("Double Backslash Brace", r"""MATCH (f:Function) WHERE f.source_code =~ ".*foo\\{.*" RETURN count(f)""")

print("Testing injection regexes with escaped quotes")
test("Double Escapes", r"""MATCH (f:Function) WHERE f.source_code =~ ".*(execute|raw_sql|cursor).*f['\"].*\\{.*}.*" RETURN count(f) LIMIT 1""")

test("Double Escapes CMD", r"""MATCH (f:Function) WHERE f.source_code =~ ".*(os\\.system|subprocess\\.call|subprocess\\.Popen|exec\\(|eval\\().*" RETURN count(f) LIMIT 1""")
