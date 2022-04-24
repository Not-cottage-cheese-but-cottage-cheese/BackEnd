import click
from datetime import datetime
from sqlalchemy.sql import text
from db import DBSession, ImageDB
from explore_images import question_generator


def next_image(favourite_id: int, id: int = -1) -> int:
    'Returns next random image ID'
    with DBSession() as session:
        return session.execute(
            text('''
            SELECT
                id 
            FROM (
                SELECT 
                    s.*,
                    sum(p) over (ORDER BY id) > r.r % sum(p) over () as f
                FROM (
                    SELECT 
                        id,
                        likes_count,
                        case 
                            when id == :favourite_id then (sum(likes_count + 1) over () - likes_count - 1)
                            else likes_count + 1
                        end as p
                    from images i 
                    where id <> :id
                ) s, (
                    SELECT ABS(RANDOM()) as r
                ) r
            ) ss
            WHERE f
            ORDER BY id
            limit 1
            '''),
            {'id': id, 'favourite_id': favourite_id}
        ).scalar()


@click.command()
def main():
    'Script that explores all images and allow to like/skip them'
    input_choices = click.Choice(['like', 'skip', 'quit'])
    favourite_id = click.prompt(
        text='Введите ID изображения "фаворита"',
        type=int,
        default=1
    )
    image_id = next_image(favourite_id=favourite_id)

    questions = question_generator()

    with DBSession() as session:
        while True:
            image: ImageDB = session.query(
                ImageDB
            ).where(
                ImageDB.id == image_id
            ).first()
            image_id = next_image(
                favourite_id=favourite_id,
                id=image_id,
            )

            command = click.prompt(
                text=(
                    '\n'
                    f'{next(questions)}\n'
                    f'ID: {image.id}\n'
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
                    image.last_update = datetime.now()
                    session.flush()
                    session.commit()
                case 'skip':
                    pass
                case 'quit':
                    click.echo('\nСпасибо за участие!')
                    return


if __name__ == '__main__':
    main()
