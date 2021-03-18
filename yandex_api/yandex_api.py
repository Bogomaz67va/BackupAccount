import requests
import os
import datetime
from time import sleep
from tqdm import tqdm
from root_dir import root_dir

"""https://oauth.yandex.ru/authorize?response_type=token&client_id=<32-значный выданный при регистрации приложения>"""


class YandexAPI:
    ROOT_DIR = root_dir()
    y_folder = {
        'resources': 'resources',
        'files_all': 'resources/files',
        'last_files': 'resources/last-uploaded',
        'file_upload': 'resources/upload',
    }

    def __init__(self, token: str):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/disk/'
        self.headers = {
            'Authorization': f'OAuth {self.token}'
        }

    def application_folder_path(self):
        """Для доступа к собственной папке приложения"""
        params = {'path': 'app:/'}
        r = requests.get(f"{self.url}{YandexAPI.y_folder['resources']}", params=params, headers=self.headers)
        return r.json()

    def user_disk_data(self):
        """API возвращает общую информацию о Диске пользователя: доступный объем, адреса системных папок и т. п."""
        """trash_size - Объем файлов, находящихся в Корзине, в байтах."""
        """total_space - Общий объем Диска, доступный пользователю, в байтах."""
        """used_space - Объем файлов, уже хранящихся на Диске, в байтах"""
        """system_folders - Абсолютные адреса системных папок Диска."""
        r = requests.get(self.url, headers=self.headers)
        return r.json()

    def files_all(self, limit=20, media_type=""):
        """API возвращает плоский список всех файлов на Диске в алфавитном порядке."""
        """принимает свойсвто limit количество файлов, по умолчанию 20"""
        """media_type = тип файла"""
        if media_type == 0:
            params = {'limit': limit}
        else:
            params = {
                'limit': limit,
                'media_type': media_type
            }
        r = requests.get(f"{self.url}{YandexAPI.y_folder['files_all']}", params=params, headers=self.headers)
        return r.json()

    def last_uploaded_files(self, limit=20, media_type=""):
        """API возвращает список последних файлов, загруженных на Диск."""
        """принимает свойсвто limit количество файлов, по умолчанию 20"""
        """media_type = тип файла"""
        if media_type == 0:
            params = {'limit': limit}
        else:
            params = {
                'limit': limit,
                'media_type': media_type
            }
        r = requests.get(f"{self.url}{YandexAPI.y_folder['last_files']}", params=params, headers=self.headers)
        return r.json()

    def folder(self, name):
        """Создание папки"""
        params = {'path': name}
        requests.put(f"{self.url}{YandexAPI.y_folder['resources']}", params=params, headers=self.headers)
        return f"Папка {name} успешна создана"

    def upload_social_network(self, file: str, folder=""):
        """Загрузка файла на Диск и создание папки и логгирование в папки с апи"""
        if len(folder) > 0:
            params_folder = {'path': folder}
            requests.put(f"{self.url}{YandexAPI.y_folder['resources']}", params=params_folder, headers=self.headers)

        try:
            file_dir_link = f"{YandexAPI.ROOT_DIR}/{file}".replace('\\', '/')
            os.chdir(file_dir_link)
        except FileNotFoundError:
            print("Не удается найти указанный файл: 'D:/Python/BackupAccount/MA/55293429'")
            exit()

        file_list = os.listdir(file_dir_link)
        dir_log = f"{YandexAPI.ROOT_DIR}/yandex_api/log/".replace('\\', '/')
        file_name = file.split('/')
        log_name = str(file_name[-1])

        print("Идет загрузка на диск...")
        for f_item in tqdm(file_list):
            if len(folder) == 0:
                params = {'path': f_item}
            else:
                params = {'path': f"{folder}/{f_item}"}
            r = requests.get(f"{self.url}{YandexAPI.y_folder['file_upload']}", params=params, headers=self.headers)

            if r.status_code == 200:
                with open(f_item, mode='rb') as f:
                    requests.put(r.json()['href'], files={"file": f})
                    if len(folder) > 0:
                        with open(f"{dir_log}{log_name}.txt", mode='a', encoding='utf-8') as f_log:
                            f_log.write(f"*** Файл {f_item} успешно сохранен на диск в папку {folder}\n")
                    else:
                        with open(f"{dir_log}{log_name}.txt", mode='a', encoding='utf-8') as f_log:
                            f_log.write(f"*** Файл {f_item} успешно сохранен на диск\n")
                    sleep(0.001)
            else:
                time_in_sec = str(datetime.datetime.now().time()).replace(':', '-').replace('.', '-')[:-4]
                f_item_new = f"{str(f_item).split('.')[0]}-{time_in_sec}.{str(f_item).split('.')[-1]}"

                if len(folder) == 0:
                    params = {'path': f_item_new}
                else:
                    params = {'path': f"{folder}/{f_item_new}"}
                r = requests.get(f"{self.url}{YandexAPI.y_folder['file_upload']}", params=params, headers=self.headers)
                with open(f_item, mode='rb') as f:
                    requests.put(r.json()['href'], files={"file": f})
                    with open(f"{dir_log}{log_name}.txt", mode='a', encoding='utf-8') as f_log:
                        f_log.write(f"--- Файл добавлен {f_item_new} с текущей датой\n")
        print("Загрузка завершена")

    def upload(self, file: str, folder=""):
        """Загрузка файла на Диск и создание папки"""
        if len(folder) > 0:
            params_folder = {'path': folder}
            requests.put(f"{self.url}{YandexAPI.y_folder['resources']}", params=params_folder, headers=self.headers)

        file_new = os.path.basename(file)
        if len(folder) == 0:
            params = {'path': file_new}
        else:
            params = {'path': f"{folder}/{file_new}"}
        r = requests.get(f"{self.url}{YandexAPI.y_folder['file_upload']}", params=params, headers=self.headers)
        if r.status_code == 200:
            href = r.json()['href']
            with open(file, mode='rb') as f:
                requests.put(href, files={"file": f})
                if len(folder) > 0:
                    return f"Файл {file_new} успешно сохранен на диск в папку {folder}"
                else:
                    return f"Файл {file_new} успешно сохранен на диск"
        else:
            return f"Файл с таким именем {file_new} уже существует"

    def delete(self, file, permanently=False):
        """Удаление файла или папки"""
        file_new = os.path.basename(file)
        if permanently:
            params = {
                'path': file_new,
                'permanently': True,
            }
        else:
            params = {'path': file_new}
        r = requests.delete(f"{self.url}{YandexAPI.y_folder['resources']}", params=params, headers=self.headers)
        if r.status_code == 204 and permanently:
            return "Файл или папка успешно удален и не помещен в корзину"
        elif r.status_code == 204:
            return "Файл или папка успешно удален и помещен в корзину"
        else:
            return "Файла или папки с таким именем не существует"
