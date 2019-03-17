import sqlite3
import json

db_conn = sqlite3.connect(':memory:')
db = db_conn.cursor()

db.execute("CREATE TABLE cache (obj_type TEXT, id INTEGER, payload TEXT)")


def decode_rows(rows):
    new_rows = []
    for row in rows:
        new_rows.append(
            (row[0], row[1], json.loads(row[2]))
        )
    return new_rows


def insert_cache(obj):
    db.execute(
        f"INSERT INTO cache (obj_type, id, payload) values ('{obj.__class__.__name__}', {obj.oid}, '{obj.json_payload}')")


def read_cache():
    db_rows = db.execute(f"SELECT * FROM cache")
    tuple_rows = decode_rows([row for row in db_rows])
    return tuple(tuple_rows)


def sync_cache(oid, cls, session):
    db_rows = db.execute(f"SELECT * FROM cache WHERE id={oid} type='{cls.__class__.__name__}'")
    tuple_rows = decode_rows([row for row in db_rows])
    if tuple_rows.__len__() == 0:
        print('Cache not found, creating new one')
        obj = cls(oid, session)
        insert_cache(obj)
    else:
        print('Cache found, returning it')
        obj = cls(oid, session, payload=tuple_rows[0][3])
        return obj
