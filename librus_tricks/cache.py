import json
import logging
import sqlite3


class SQLiteCache:
    def __init__(self, db_location='cache.sqlite'):
        # TODO: Dodać możliwość wyłączenia cache'ownia (każda rzecz jest pobierana z serwera)
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
        logging.debug(f'Checking existence of object {cls.__name__} with id {oid}')
        cache_response = self.get_object(oid, cls.__name__)
        if cache_response == None:
            logging.debug(f'Object not found, creating new one')
            # print(f'Tworzę kopię dla {oid}')
            c = cls(oid, session)
            self.insert_and_commit(c.oid, c.__class__.__name__, json.dumps(c._json_payload, ensure_ascii=True))
            logging.debug(f'Object created')
            return c
        else:
            logging.debug(f'Object found, using cached data')
            return cls(cache_response[0], session, json.loads(cache_response[2]))
