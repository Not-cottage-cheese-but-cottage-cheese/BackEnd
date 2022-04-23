import uvicorn
import traceback
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from db import DBSession, ImageDB
from download_images import download_images as download_images_on_disk
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


if __name__ == '__main__':
    uvicorn.run('api:app', port=4000, reload=settings.RELOAD)
