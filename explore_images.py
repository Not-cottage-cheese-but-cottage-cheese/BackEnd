import random
import click
from sqlalchemy.sql import text
from db import DBSession, ImageDB


def get_first_image_in_album(album_id: int) -> int:
    with DBSession() as session:
        return session.execute(
            text('''
            SELECT 
                id
            FROM 
                images i 
            WHERE 
                album_id = :album_id
            ORDER BY 
                album_position
            LIMIT 1
            '''),
            {'album_id': album_id}
        ).scalar()


def next_image_in_album(id: int) -> int:
    'Returns next image ID (returns first after last)'
    with DBSession() as session:
        return session.execute(
            text('''
            SELECT 
                next_id
            FROM (
                SELECT
                    id as id,
                    COALESCE(
                        LEAD(id) OVER (PARTITION BY album_id ORDER BY album_position),
                        FIRST_VALUE(id) OVER (PARTITION BY album_id ORDER BY album_position)
                    ) AS next_id,
                    album_id AS album_id 
                FROM 
                    images i 
            ) s
            WHERE 
                id = :id
            '''),
            {'id': id}
        ).scalar()


def question_generator():
    yield 'Как вам данная картинка?'

    options = [
        'Как вам данная картинка?',
        'Как вам данная картинка?',
        'Как вам данная картинка?',
        'Как вам данная картинка?',
        'Как вам данная картинка?',
        'Как вам данная картинка?',
        'А как вам данная картинка?',
        'А как вам данная картинка?',
        'А как вам данная картинка?',
        'А как вам данная картинка?',
        'А как вам данная картинка?',
        'А эта?',
        'А эта?',
        'А эта?',
        'А вот эта?',
        'Мне кажется, что эта картинка вам понравится...',
        'Вам нравится данное изображение?',
        'Эта точно в вашем вкусе!',
        'Смейся или бан.',
    ]
    while True:
        yield random.choice(options)


@click.command()
@click.option("--album-id", default=281940823, show_default=True, help="ID альбома")
def main(album_id: int):
    'Script that explores images in album and allow to like/skip images'
    input_choices = click.Choice(['like', 'skip', 'quit'])
    first_image_id = get_first_image_in_album(album_id)
    image_id = first_image_id

    questions = question_generator()

    with DBSession() as session:
        while True:
            image: ImageDB = session.query(
                ImageDB
            ).where(
                ImageDB.id == image_id
            ).first()
            image_id = next_image_in_album(image_id)

            command = click.prompt(
                text=(
                    '\n'
                    f'{next(questions)}\n'
                    f'Ссылка: {image.url}\n'
                    f'Автор: {image.author_name}\n'
                    f'Число лайков: {image.likes_count}\n'
                    f'Вы решаете:'
                ),
                default='skip',
                type=input_choices,
                show_choices=True,
                show_default=True,
            )
            match command:
                case 'like':
                    image.likes_count += 1
                    session.flush()
                    session.commit()
                case 'skip':
                    pass
                case 'quit':
                    click.echo('\nСпасибо за участие!')
                    return
            if image_id == first_image_id:
                if not click.confirm(
                    '\nВы просмотрели все изображения в альбоме, хотите продолжить?',
                    default=True,
                ):
                    click.echo('\nСпасибо за участие!')
                    return


if __name__ == '__main__':
    main()
