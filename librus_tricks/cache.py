from sqlalchemy import create_engine, String, JSON, Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

class SkeletonCache:
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

class CacheManager(SkeletonCache):
    Base = declarative_base()
    def __init__(self, engine_uri='sqlite:///cache.sqlite'):
        engine = create_engine(engine_uri)

        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        self.session = Session()
        self.Base.metadata.create_all(engine)

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

    def add_object(self, uid, cls, resource):
        self.session.add(
            self.ObjectLoadCache(uid, cls.__name__, resource)
        )
        self.session.commit()

    def get_object(self, uid, cls):
        response = self.session.query(self.ObjectLoadCache).filter_by(uid=uid, name=cls.__name__).first()
        return cls.assembly(uid, response)

    def add_query(self, uri, response):
        self.session.add(
            self.APIQueryCache(uri=uri, response=response, last_load=datetime.now())
        )
        self.session.commit()

    def get_query(self, uri):
        """

        :rtype: CacheManager.APIQueryCache
        """
        return self.session.query(self.APIQueryCache).filter_by(uri=uri).first()

    def del_query(self, uri):
        self.session.query(self.APIQueryCache).filter_by(uri=uri).delete()
        self.session.commit()


cache_manager = CacheManager()