from collections import Counter
from time import sleep

import datetime
import os
import requests
import json
from tqdm import tqdm

from root_dir import root_dir


class VkApi:
    ROOT_DIR = root_dir()

    def __init__(self, token: str, id):
        self.token = token
        self.url = 'https://api.vk.com/method/'
        self.v = '5.130'

        self.users_album = []
        self.result_users = []
        self.true_id_album = []

        self.title_album = ''

        r = requests.get(f'{self.url}users.get', params={
            'access_token': self.token,
            'v': self.v,
            'user_ids': id
        })
        try:
            is_closed = r.json()['response']
        except KeyError:
            print('Ошибка авторизации пользователя: срок действия access_token истек')
            exit()

        for item_is in is_closed:
            print(f"Имя: {item_is['first_name']}, Фамилия: {item_is['last_name']}, id: {item_is['id']}")
            if item_is['first_name'] == 'DELETED' or item_is['is_closed']:
                self.id = 1
                print(f"Аккаунт {id} - приватный!(Для методов будет выводиться Пашка Дуров!")
            else:
                self.id = id

        self.params = {
            'access_token': self.token,
            'v': self.v,
        }

    def users_is_closed(self):
        """проверка на приватность"""
        self.params['user_ids'] = self.id
        print(self.params)
        r = requests.get(f"{self.url}users.get", params=self.params)
        is_closed = r.json()['response'][0]['is_closed']
        if is_closed:
            return f'Данный {self.id} аккаунт является приватным'
        else:
            return f'Публичный аккаунт'

    def photos_get_Albums(self, count=5):
        """Возвращает информацию по альбомам в users_album и id альбома для дальнейшей проверки true_id_album"""
        params = {
            'access_token': self.token,
            'v': self.v,
            'owner_id': self.id,
            'count': count,
            'need_system': '1',
        }
        r = requests.get(f"{self.url}photos.getAlbums", params=params)

        try:
            if r.json()['response']['items'] is not None:
                for item in r.json()['response']['items']:
                    self.users_album.append({
                        'album_id': item['id'],
                        'size_album': item['size'],
                        'title_album': item['title'],
                    })
                    self.true_id_album.append(item['id'])
            else:
                print("Фотографий нет")
        except KeyError:
            print("В доступе отказано")

    def photos_get(self, id_album: str, count=5):
        """Возвращает список фотографий в конкретном альбоме по умолчанию 5"""

        if int(id_album) in self.true_id_album:
            self.params['owner_id'] = self.id
            self.params['album_id'] = id_album
            self.params['extended'] = '1'
            self.params['count'] = count
            self.params['rev'] = '0'

            try:
                r = requests.get(f"{self.url}photos.get", params=self.params)
                for items in r.json()['response']['items']:
                    url = items['sizes'][:][-1]['url']
                    link_date_text = f"{str(url).split('&')[2]}"
                    # это надо здесь сделать иначе программа будет не универсальная
                    microsecond = []
                    for i in link_date_text:
                        if i.isdigit():
                            microsecond.append(int(i))
                    size = items['sizes'][:][-1]['type']
                    date_album = items['date']
                    date = datetime.datetime.fromtimestamp(date_album)
                    for micro_time in microsecond[:3]:
                        data_valid = date.strftime(f'%Y-%m-%d %H:%M:%S{micro_time}')
                    likes = items['likes']['count']
                    self.result_users.append({
                        'likes': likes,
                        'date': data_valid.replace(':', '_'),
                        'size': size,
                        'url': url,
                    })
                    sleep(0.001)
            except KeyError:
                print('Введите токен с правами на фото')
        else:
            print("Введите правильный номер альбома")

    def show_album(self):
        """Просмотр информации по альбомам пользователя"""
        for items in self.users_album:
            print(f"Номер альбома: {items['album_id']}\n"
                  f"Количество фото: {items['size_album']}\n"
                  f"Название: {items['title_album']}\n")

    def save_photos(self, file_path: str):
        """Cохранение фотографий в папку с программой и сохранение лог файла в папку с апи вк"""
        os.chdir(VkApi.ROOT_DIR)
        try:
            os.makedirs(f"{file_path}/{str(self.id)}")
        except FileExistsError:
            print('')
        str_f = f"{VkApi.ROOT_DIR}/{file_path}/{str(self.id)}".replace("\\", "/")

        dir_log = f"{VkApi.ROOT_DIR}/vk_api/log/".replace('\\', '/')
        log_name = str(self.id)
        with open(f"{dir_log}{log_name}.json", mode='a', encoding='utf-8') as f_w:
            f_w.close()

        likes = []
        file_json = []

        for item in self.result_users:
            likes.append(item['likes'])
        likes_repeat = [k for k, v in Counter(likes).items() if v > 1]
        if likes_repeat is not None:
            for item_photo in tqdm(self.result_users):
                if item_photo['likes'] not in likes_repeat:
                    file_name = str(item_photo['likes'])
                    file_json.append({
                        'file_name': file_name,
                        'size': self.result_users[0]['size']
                    })
                    response = requests.get(item_photo['url'])
                    out = open(f"{str_f}/{file_name}.jpg", "wb")
                    out.write(response.content)
                    out.close()

                else:
                    file_name = str(f"{item_photo['likes']}_{item_photo['date']}")
                    file_json.append({
                        'file_name': file_name,
                        'size': self.result_users[0]['size']
                    })
                    response = requests.get(item_photo['url'])
                    out = open(f"{str_f}/{file_name}.jpg", "wb")
                    out.write(response.content)
                    out.close()
                sleep(0.1)
        else:
            print('error')

        if log_name:
            with open(f"{dir_log}{log_name}.json", mode='a', encoding='utf-8') as f_w:
                json.dump(file_json, f_w)
                f_w.close()
        else:
            print('error')
