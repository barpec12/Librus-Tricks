from sqlalchemy import create_engine, String, JSON, Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.pool import StaticPool
import json
import logging
import sqlite3


class CacheBase:
    def add_object(self, *args, **kwargs):
        pass

    def get_object(self, *args, **kwargs):
        raise Exception('Not implemented')

    def del_object(self, *args, **kwargs):
        raise Exception('Not implemented')

    def add_query(self, *args, **kwargs):
        pass

    def get_query(self, *args, **kwargs):
        raise Exception('Not implemented')

    def del_query(self, *args, **kwargs):
        raise Exception('Not implemented')


class DumbCache(CacheBase):
    def sync(self, oid, cls, session):
        return cls(oid, session)


class AlchemyCache(CacheBase):
    Base = declarative_base()

    def __init__(self, engine_uri='sqlite:///cache.sqlite'):
        engine = create_engine(engine_uri, connect_args={'check_same_thread': False}, poolclass=StaticPool)

        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        self.session = Session()
        self.Base.metadata.create_all(engine)
        self.syn_session = None

    class APIQueryCache(Base):
        __tablename__ = 'uri_cache'

        uri = Column(String, primary_key=True)
        response = Column(JSON)
        last_load = Column(DateTime)

    class ObjectLoadCache(Base):
        __tablename__ = 'object_cache'

        uid = Column(Integer, primary_key=True)
        name = Column(String)
        resource = Column(JSON)
        last_load = Column(DateTime)

    def add_object(self, uid, cls, resource):
        self.session.add(
            self.ObjectLoadCache(uid=uid, name=cls.__name__, resource=resource, last_load=datetime.now())
        )
        self.session.commit()

    def get_object(self, uid, cls):
        """

        :rtype: AlchemyCache.ObjectLoadCache
        """
        response = self.session.query(self.ObjectLoadCache).filter_by(uid=uid, name=cls.__name__).first()
        if response is None:
            return None
        return cls.assembly(response.resource, self.syn_session)

    def add_query(self, uri, response):
        self.session.add(
            self.APIQueryCache(uri=uri, response=response, last_load=datetime.now())
        )
        self.session.commit()

    def get_query(self, uri):
        """

        :rtype: AlchemyCache.APIQueryCache
        """
        return self.session.query(self.APIQueryCache).filter_by(uri=uri).first()

    def del_query(self, uri):
        self.session.query(self.APIQueryCache).filter_by(uri=uri).delete()
        self.session.commit()

    def del_object(self, uid):
        self.session.query(self.ObjectLoadCache).filter_by(uid=uid).delete()
        self.session.commit()


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
            );
            '''
        )
        self.cur.execute(
            '''
            create table messages
            (
            	url text not null,
            	header text not null,
            	message text,
            	author text,
            	date int
            );
            '''
        )

    def delete_table(self):
        self.cur.execute(
            "drop table cache; drop table messages"
        )

    # noinspection SqlWithoutWhere
    def clear_table(self):
        self.cur.execute(
            "delete from cache; delete from messages"
        )
        self.commit()

    def insert(self, oid, class_name, json_payload):
        self.cur.execute(
            f"insert into cache (object_id, class_name, json_payload) values ({oid}, '{class_name}', '{json_payload}');"
        )

    def insert_message(self, url, message, author, timestamp, header):
        self.cur.execute(
            f"insert into messages (url, message, author, date, header) values ('{url}', '{message}', '{author}', {timestamp}, '{header}');"
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

    def get_message(self, url):
        response = self.cur.execute(
            f"select * from messages where url='{url}'"
        ).fetchone()
        return response

    def sync(self, oid, cls, session):
        logging.debug(f'Checking existence of object {cls.__name__} with id {oid}')
        cache_response = self.get_object(oid, cls.__name__)
        if cache_response is None:
            logging.debug(f'Object not found, creating new one')
            c = cls(oid, session)
            self.insert_and_commit(c.oid, c.__class__.__name__, json.dumps(c._json_payload, ensure_ascii=True))
            logging.debug(f'Object created')
            return c
        else:
            logging.debug(f'Object found, using cached data')
            return cls(cache_response[0], session, json.loads(cache_response[2]))

    def sync_message(self, message_obj):
        """

        :type message_obj: librus_tricks.messages.SynergiaScrappedMessage
        """
        cache_response = self.get_message(message_obj.url)
        if cache_response is None:
            message_text = message_obj.read_from_server()
            self.insert_message(message_obj.url, message_text, message_obj.author_alias,
                                int(message_obj.msg_date.timestamp()), message_obj.header)
            return message_text
        else:
            return cache_response[2]
