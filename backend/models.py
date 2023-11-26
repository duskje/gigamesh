import os

from sqlalchemy.orm import declarative_base, relationship, backref, sessionmaker, scoped_session, Query, Mapped, \
    joinedload
from sqlalchemy import Column, Table, Integer, String, create_engine, ForeignKey, asc, DateTime, Float, JSON
from sqlalchemy.sql import functions
from definitions import DEFAULT_DATABASE_PATH

engine = create_engine(f'sqlite:///{DEFAULT_DATABASE_PATH}', echo=False)
Base = declarative_base()


def create_database():
    Base.metadata.create_all(engine)


def reset_database():
    try:
        os.remove(DEFAULT_DATABASE_PATH)
    except FileNotFoundError:
        pass

    create_database()


class Song(Base):
    __table__ = 'songs'

    song_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    setlist_id = Column(ForeignKey('setlist.setlist_id'))
    setlist = relationship('setlist', back_populates='songs')

    configuration_data = Column(JSON)


class Setlist(Base):
    __table__ = 'setlist'

    setlist_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    songs = relationship('songs', back_populates='setlist')

