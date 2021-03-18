from vk_api.vk_api import VkApi
from yandex_api.yandex_api import YandexAPI

if __name__ == '__main__':
    y = YandexAPI('<TOKEN_YANDEX>')
    v = VkApi('<TOKEN_VK>', 552934290)
    # v.photos_get_Albums()
    # v.show_album()
    # v.photos_get('-6')
    # v.save_photos('VK')
    # y.upload_social_network('VK/552934290', 'VK')
