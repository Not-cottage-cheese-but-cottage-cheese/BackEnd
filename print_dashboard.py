from typing import Any
from datetime import datetime, timedelta
import click
import pytermgui as ptg
from settings import settings
from db import DBSession, ImageDB


class TopTableWidget(ptg.Widget):

    def __init__(self, n: int, framerate: int, **attrs: Any) -> None:
        super().__init__(**attrs)
        self.n = n
        self.framerate = framerate
        self.last_update = datetime.now()
        self.table_lines = self.query_lines()

    def query_lines(self) -> list[str]:
        with DBSession() as session:
            images: list[ImageDB] = (
                session
                .query(ImageDB)
                .order_by(ImageDB.likes_count.desc())
                .limit(self.n)
                .all()
            )

            return [
                f'Время обновления: {datetime.now()}',
                '',
                f'{"ID":^4}|{"Автор":^25}|Лайки|{"Путь":^35}',
                f'{"-"*4}+{"-"*25}+{"-"*5}+{"-"*35}',
            ] + [
                f'''{
                    image.id:>4}|{
                    image.author_name[:25]:>25}|{
                    min(image.likes_count, 99999):>5}|{
                    image.path[:35]:>35}'''
                for image in images
            ]

    def get_lines(self) -> list[str]:
        if datetime.now() > self.last_update + timedelta(seconds=1/self.framerate):
            self.last_update = datetime.now()
            self.table_lines = self.query_lines()

        return self.table_lines


class LastTableWidget(ptg.Widget):

    def __init__(self, n: int, framerate: int, **attrs: Any) -> None:
        super().__init__(**attrs)
        self.n = n
        self.framerate = framerate
        self.last_update = datetime.now()
        self.table_lines = self.query_lines()

    def query_lines(self) -> list[str]:
        with DBSession() as session:
            images: list[ImageDB] = (
                session
                .query(ImageDB)
                .order_by(ImageDB.last_update.desc())
                .where(ImageDB.last_update.isnot(None))
                .limit(self.n)
                .all()
            )

            return [
                f'{"Прошло времени":^20}|{"ID":^4}|{"Автор":^25}|Лайки|{"Путь":^35}',
                f'{"-"*20}+{"-"*4}+{"-"*25}+{"-"*5}+{"-"*35}',
            ] + [
                f'''{
                    str(datetime.now() - image.last_update)[:20]:>20}|{
                    image.id:>4}|{
                    image.author_name[:25]:>25}|{
                    min(image.likes_count, 99999):>5}|{
                    image.path[:35]:>35}'''
                for image in images
            ] + [
                f'{" "*20}+{" "*4}+{" "*25}+{" "*5}+{" "*35}'
                for _ in range(self.n - len(images))
            ]

    def get_lines(self) -> list[str]:
        if datetime.now() > self.last_update + timedelta(seconds=1/self.framerate):
            self.last_update = datetime.now()
            self.table_lines = self.query_lines()

        return self.table_lines


@click.command()
@click.option('-n', default=5, show_default=True, help='Количество изображений в топе')
@click.option('-k', default=5, show_default=True, help='Количество изображений в последних')
@click.option('--secret', type=str, required=True, help='Секрет для доступа к топу')
def main(n: int, k: int, secret: str):
    """Script prints images dashboard"""

    if secret != settings.SECRET:  # Yes, yes, not safe
        click.echo('Invalid secret!', err=True)
        exit(1)

    with ptg.WindowManager() as manager:
        window = ptg.Window(
            f'[210 bold]TОП {n} изображений',
            '',
            TopTableWidget(n=n, framerate=1),
            '',
            f'[210 bold]Последние {k} лайкнутых изображений',
            '',
            LastTableWidget(n=k, framerate=1),
            width=105,
            height=n+k+10,
        )
        manager.add(window)
        manager.run()


if __name__ == '__main__':
    main()
