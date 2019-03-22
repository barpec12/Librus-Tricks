import sqlite3
import json


class Cache:
    def __init__(self, db_location='cache.sqlite'):
        db_conn = sqlite3.connect(db_location)
        self.cur = db_conn.cursor()

        try:
            self.create_table()
        except sqlite3.OperationalError as oe:
            if not str(oe) == 'table cache already exists':
                raise oe
            else:
                pass

    def create_table(self):
        self.cur.execute(
            '''create table cache
(
	object_id int not null,
	class_name text not null,
	json_payload text not null
);'''
        )

    def delete_table(self):
        self.cur.execute(
            "drop table cache"
        )

    # noinspection SqlWithoutWhere
    def clear_table(self):
        self.cur.execute(
            "delete from cache"
        )
        self.commit()

    def insert(self, oid, class_name, json_payload):
        self.cur.execute(
            f"insert into cache (object_id, class_name, json_payload) values ({oid}, '{class_name}', '{json_payload}');"
        )

    def commit(self):
        self.cur.execute('commit')

    def insert_and_commit(self, oid, class_name, json_payload):
        self.insert(oid, class_name, json_payload)
        self.commit()

    def get_object(self, oid, class_name):
        response = self.cur.execute(
            f"select * from cache where object_id={oid} and class_name='{class_name}'"
        ).fetchone()
        return response

    def sync(self, oid, cls, session):
        cache_response = self.get_object(oid, cls.__name__)
        if cache_response == None:
            print(f'Tworzę kopię dla {oid}')
            c = cls(oid, session)
            self.insert_and_commit(c.oid, c.__class__.__name__, json.dumps(c._json_payload, ensure_ascii=True))
            return c
        else:
            print(f'Znaleziono kopię dla {oid}')
            return cls(cache_response[0], session, json.loads(cache_response[2]))


if __name__ == '__main__':
    from librus_tricks import aio, SynergiaClient, utilities, SynergiaTeacher

    session = SynergiaClient(aio('krystian@postek.eu', '$Un10ck_lib'))
    # grades = session.get_grades((27208160, 24040273, 21172894))[0]

    cache = Cache()

    for n in utilities.get_objects(session, 'Users', '', 'Users', SynergiaTeacher):
        k = cache.sync(n.oid, n.__class__, session)
        print(str(k.name) + ' ' + str(k.last_name))
