import click
import sqlalchemy as sqla
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///db.db', echo=False)
DBSession = sessionmaker(engine)


Base = declarative_base()


class ImageDB(Base):
    __tablename__ = 'images'

    album_id = Column(sqla.Integer, primary_key=True)
    image_id = Column(sqla.Integer, primary_key=True)
    author_id = Column(sqla.Integer)
    author_name = Column(sqla.String(512))
    likes_count = Column(sqla.Integer)
    url = Column(sqla.String(2048))  # image url
    path = Column(sqla.String(2048))  # file path


@click.command()
def main():
    """Script that creates SQLite database with tables"""
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
