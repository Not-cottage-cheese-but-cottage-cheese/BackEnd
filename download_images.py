import click
from time import sleep
import requests
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from vk_api import get_images, get_users
from db import DBSession, ImageDB
from settings import settings


def images_generator(
    owner_id: int,
    album_id: int,
    print_info: bool = True,
):
    images_info = get_images(
        owner_id=owner_id,
        album_id=album_id,
        count=0
    )
    images_count = images_info["count"]
    signs_count = len(str(images_count))

    if print_info:
        click.echo(f'В альбоме всего {images_count} мемов:')

    batch = []

    for i in range(images_count):
        if i % settings.IMAGES_BATCH_SIZE == 0:
            batch = get_images(
                owner_id=owner_id,
                album_id=album_id,
                offset=i,
                count=settings.IMAGES_BATCH_SIZE
            )['items']

        image = batch[i % settings.IMAGES_BATCH_SIZE]

        image_id = image['id']
        user_id = image['user_id']
        user_info = get_users(users_ids=[user_id])[0]
        user_name = f'{user_info["first_name"]} {user_info["last_name"]}'
        likes_count = image['likes']['count']
        url = sorted(
            image['sizes'],
            key=lambda s: s['height'] * s['width']
        )[-1]['url']
        path = f'{settings.IMAGES_PATH}/{album_id}/{image_id}.jpg'

        if print_info:
            click.echo(
                f'({i+1:{signs_count}}/{images_count:{signs_count}}) '
                f'{user_name} (https://vk.com/id{user_id}) '
                f'получил {likes_count} лайк(-ов) за мем {url}'
            )

        yield ImageDB(
            album_id=album_id,
            album_position=i,
            image_id=image_id,
            author_id=user_id,
            author_name=user_name,
            likes_count=likes_count,
            url=url,
            path=path,
        )


def download_images(owner_id: int, album_id: int, print_info: bool):
    Path(f'{settings.IMAGES_PATH}/{album_id}').mkdir(parents=True, exist_ok=True)

    with DBSession() as session:
        for image in images_generator(
            owner_id=owner_id,
            album_id=album_id,
            print_info=print_info,
        ):
            try:
                session.add(image)
                session.flush()
                session.commit()
            except IntegrityError:
                session.rollback()
                if print_info:
                    click.echo('Данное изображение уже есть в базе')
            else:
                img = requests.get(image.url).content
                with open(image.path, 'wb') as f:
                    f.write(img)

            sleep(0.25)  # antiDDOS


@click.command()
@click.option("--owner-id", default=-197700721, show_default=True, help="ID владельца альбома")
@click.option("--album-id", default=281940823, show_default=True, help="ID альбома")
@click.option("--no-print-info", default=False, is_flag=True, help="Скрыть доп. информацию с консоли")
def main(owner_id: int, album_id: int, no_print_info: bool):
    """Script that downloads images"""
    download_images(
        owner_id=owner_id,
        album_id=album_id,
        print_info=not no_print_info
    )


if __name__ == '__main__':
    main()
