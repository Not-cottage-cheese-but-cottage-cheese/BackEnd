import click
import sqlalchemy as sqla
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///db.db', echo=False)
DBSession = sessionmaker(engine)


Base = declarative_base()


class ImageDB(Base):
    __tablename__ = 'images'

    id = Column(sqla.Integer(), primary_key=True, autoincrement=True)
    album_id = Column(sqla.Integer)
    album_position = Column(sqla.Integer)
    image_id = Column(sqla.Integer)
    author_id = Column(sqla.Integer)
    author_name = Column(sqla.String(512))
    likes_count = Column(sqla.Integer)
    url = Column(sqla.String(2048))  # image url
    path = Column(sqla.String(2048))  # file path

    __table_args__ = (
        sqla.UniqueConstraint('album_id', 'image_id', name='unique_image'),
    )


@click.command()
def main():
    """Script that creates SQLite database with tables"""
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
