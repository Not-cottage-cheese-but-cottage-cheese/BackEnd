import requests
from settings import settings


def get_images(
    owner_id: int,
    album_id: int,
    offset: int = 0,
    count: int = 50
) -> dict:
    res = requests.get(
        'https://api.vk.com/method/photos.get',
        params={
            'access_token': settings.ACCESS_TOKEN,
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': 1,
            'photo_sizes': 1,
            'v': '5.131',
            'offset': offset,
            'count': count,
        }
    )
    if res.status_code != 200:
        raise Exception(f'{res}: {res.text}')

    try:
        return res.json()['response']
    except:
        raise Exception(f'{res}: {res.text}')


def get_users(
    users_ids: list[int] | set[int]
) -> list:
    res = requests.get(
        'https://api.vk.com/method/users.get',
        params={
            'access_token': settings.ACCESS_TOKEN,
            'user_ids': ','.join(map(str, users_ids)),
            'v': '5.131',
        }
    )
    if res.status_code != 200:
        raise Exception(f'{res}: {res.text}')

    try:
        return res.json()['response']
    except:
        raise Exception(f'{res}: {res.text}')
