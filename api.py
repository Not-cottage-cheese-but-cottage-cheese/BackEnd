import uvicorn
import traceback
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from db import DBSession, ImageDB
from download_images import download_images as download_images_on_disk
from explore_images import (
    next_image_in_album,
    get_first_image_in_album as get_first_image_in_album_from_db,
)
from explore_images_v2 import next_image
from settings import settings

app = FastAPI(
    title='Не творог, а творог',
    description='Решение Back End задач'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path='/api/download_images',
    description='Загружает изображения из альбома',
    tags=['10'],
)
def download_images(
    owner_id: int = Query(-197700721, description='ID владельца альбома'),
    album_id: int = Query(281940823, description='ID альбома'),
):
    try:
        download_images_on_disk(
            owner_id=owner_id,
            album_id=album_id,
            print_info=False,
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Exception: {ex}\n\nTraceback: {traceback.format_exc()}'
        )
    return True


@app.get(
    path='/api/print_images',
    description='Возвращает список загруженных изображений',
    tags=['10'],
)
def print_images():
    with DBSession() as session:
        return jsonable_encoder(
            session.query(ImageDB).all()
        )


@app.get(
    path='/api/get_first_image_in_album',
    description='Возвращает первое изображение из альбома',
    tags=['20'],
)
def get_first_image_in_album(
    album_id: int = Query(281940823, description='ID альбома'),
) -> dict:
    id = get_first_image_in_album_from_db(album_id)

    if id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого альбома нет в базе. Возможно, вам нужно его загрузить.'
        )

    with DBSession() as session:
        return jsonable_encoder(
            session
            .query(ImageDB)
            .where(ImageDB.id == id)
            .first()
        )


@app.get(
    path='/api/like_image',
    description='Лайкает изображение и возвращает следующее изображение в альбоме (циклически)',
    tags=['20'],
)
def like_image(
    id: int = Query(..., description='ID изображения')
) -> dict:
    next_id = next_image_in_album(id)

    if next_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого изображения нет в базе.'
        )

    with DBSession() as session:
        image: ImageDB = (
            session
            .query(ImageDB)
            .where(ImageDB.id == id)
            .first()
        )
        image.likes_count += 1
        image.last_update = datetime.now()
        session.flush()
        session.commit()

        return jsonable_encoder(
            session
            .query(ImageDB)
            .where(ImageDB.id == next_id)
            .first()
        )


@app.get(
    path='/api/skip_image',
    description='Возвращает следующее изображение в альбоме (циклически)',
    tags=['20'],
)
def skip_image(
    id: int = Query(..., description='ID изображения')
) -> dict:
    next_id = next_image_in_album(id)

    if next_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Такого изображения нет в базе.'
        )

    with DBSession() as session:
        return jsonable_encoder(
            session
            .query(ImageDB)
            .where(ImageDB.id == next_id)
            .first()
        )


@app.get(
    path='/api/like_image_v2',
    description='Лайкает изображение и возвращает следующее случайное изображение',
    tags=['30'],
)
def like_image_v2(
    id: int = Query(..., description='ID изображения'),
    favourite_id: int = Query(..., description='ID изображения "фаворита"'),
) -> dict:
    next_id = next_image(favourite_id=favourite_id, id=id)

    with DBSession() as session:
        image: ImageDB = (
            session
            .query(ImageDB)
            .where(ImageDB.id == id)
            .first()
        )
        image.likes_count += 1
        image.last_update = datetime.now()
        session.flush()
        session.commit()

        return jsonable_encoder(
            session
            .query(ImageDB)
            .where(ImageDB.id == next_id)
            .first()
        )


@app.get(
    path='/api/skip_image_v2',
    description='Возвращает следующее случайное изображение',
    tags=['30'],
)
def skip_image_v2(
    id: int = Query(-1, description='ID изображения (-1 получения случайного изображения)'),
    favourite_id: int = Query(..., description='ID изображения "фаворита"'),
) -> dict:
    next_id = next_image(
        favourite_id=favourite_id,
        id=id,
    )

    with DBSession() as session:
        return jsonable_encoder(
            session
            .query(ImageDB)
            .where(ImageDB.id == next_id)
            .first()
        )


@app.get(
    path='/api/print_dashboard',
    description='Возвращает дашборд изображений',
    tags=['50'],
)
def top_images(
    n: int = Query(5, description='Количество изображений в топе'),
    k: int = Query(5, description='Количество изображений в последних'),
    secret: str = Query(
        'secret',
        description='Секрет для доступа к дашборду (по умолчанию "secret")'
    )
):
    if secret != settings.SECRET:  # Yes, yes, not safe
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid secret',
        )

    with DBSession() as session:
        return {
            'top': jsonable_encoder(
                session
                .query(ImageDB)
                .order_by(ImageDB.likes_count.desc())
                .limit(n)
                .all()
            ),
            'last': jsonable_encoder(
                session
                .query(ImageDB)
                .order_by(ImageDB.last_update.desc())
                .where(ImageDB.last_update.isnot(None))
                .limit(k)
                .all()
            )
        }


if __name__ == '__main__':
    uvicorn.run('api:app', port=4000, reload=settings.RELOAD)
