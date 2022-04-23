import click
from db import DBSession, ImageDB


@click.command()
def main():
    """Script prints all images from database"""

    with DBSession() as session:
        images: list[ImageDB] = session.query(ImageDB).all()
        count = len(images)
        count_signs = len(str(count))
        for i, image in enumerate(images, start=1):
            click.echo(
                f'({i:{count_signs}}/{count:{count_signs}}) '
                f'{image.author_name} (https://vk.com/id{image.author_id}) '
                f'получил {image.likes_count} лайк(-ов) за мем {image.url}'
            )


if __name__ == '__main__':
    main()
