def to_lang(language: str):
    match language:
        case 'ru':
            return 'ru'
        case _:
            return 'en'

languages = ['en', 'ru']

# --- Bot ---

version = {
    'en': 'Bot version',
    'ru': 'Версия бота',
}

last_update_date = {
    'en': 'Bot last update date',
    'ru': 'Дата последнего обновления',
}

bot_description = {
    'en': """
Hi! This bot allows you to download YouTube videos/audios (up to 2 GB in size) using their links. You can also download music with **premium** quality from YouTube Music if such streams are available.

Just send me a YouTube link, for example:
https://www.youtube.com/watch?v=letters
https://youtube.com/shorts/letters
https://youtu.be/letters
https://music.youtube.com/watch?v=letters

Some other services are supported too.
Yandex Music:
https://music.yandex.com/album/000/track/000
https://music.yandex.ru/album/000/track/000
Dzen:
soon...

Message @GidRadium if you want to add more services.

Use /settings to change language, captions and /share option.
""",
    'ru': """
Привет! Этот бот позволяет скачивать видео/аудио с YouTube (до 2 ГБ) по их ссылкам. Вы также можете скачать музыку премиум-качества с YouTube Music, если такие потоки доступны.

Просто отправьте мне ссылку на YouTube, например:
https://www.youtube.com/watch?v=letters
https://youtube.com/shorts/letters
https://youtu.be/letters
https://music.youtube.com/watch?v=letters

Поддерживаются и другие сервисы:
Yandex Music:
https://music.yandex.com/album/000/track/000
https://music.yandex.ru/album/000/track/000
Dzen:
скоро...

Обращайтесь к @GidRadium, если хотите добавить больше сервисов.

Используйте /settings, чтобы изменить язык, подписи и настройку /share.
""",
}

bot_updated_recently = {
    'en': 'Bot has been updated recently. See new settings added. (/settings)',
    'ru': 'Бот недавно обновился! Посмотрите настройки, которые добавились. (/settings)',
}

searching = {
    'en': '_Searching..._',
    'ru': '_Поиск..._',
}

downloading = {
    'en': 'Downloading',
    'ru': 'Скачивание',
}

uploading = {
    'en': 'Uploading',
    'ru': 'Отправка',
}

# Settings

default_settings_description = {
    'en': 'Default settings:',
    'ru': 'Настройки по умолчанию:',
}

default_language = {
    'en': 'Language',
    'ru': 'Язык',
}

default_audio_caption = {
    'en': 'Audio caption',
    'ru': 'Подпись к аудио',
}

default_video_caption = {
    'en': 'Video caption',
    'ru': 'Подпись к видео',
}

default_post_caption = {
    'en': 'Post caption',
    'ru': 'Подпись к посту',
}

default_caption_options = {
    '---': {
        'en': '---',
        'ru': '---',
    },
    'title': {
        'en': 'title',
        'ru': 'название',
    },
    'source': {
        'en': 'source',
        'ru': 'источник',
    },
    'title+source': {
        'en': 'title+source',
        'ru': 'название+источник',
    },
}

default_share_status = {
    'en': 'Allow /share',
    'ru': 'Разрешить /share',
}

allow_press_buttons = {
    'en': 'Allow press buttons',
    'ru': 'Разрешить нажатие кнопок',
}

alert_press_buttons = {
    'en': 'Message owner has not allowed the buttons to be used by other users.',
    'ru': 'Владелец сообщения не разрешил использование кнопок другими пользователями.',
}

# Errors

err_message_empty = {
    'en': 'Message text is empty.',
    'ru': 'Текст сообщения отсутствует.',
}

err_not_link = {
    'en': 'It is not a link.',
    'ru': 'Это не ссылка.',
}

err_no_link_support = {
    'en': "Don't support this type of links. Message @GidRadium if you want them to be added.",
    'ru': 'Не поддерживаю такой тип ссылок. Напишите об этом @GidRadium, если хотите добавить их поддержку.',
}

err_not_defined = {
    'en': 'Not defined.',
    'ru': 'Не определено.',
}

err_media_not_found = {
    'en': "Can't find this media.",
    'ru': "Не могу найти это медиа."
}

err_download_media = {
    'en': "Media download error.",
    'ru': "Ошибка загрузки медиа."
}

err_upload_media = {

}

err_unknown_command = {
    'en': "Unknown command.",
    'ru': "Неизвестная команда."
}

err_generate_response = {
    'en': "Error while generating response.",
    'ru': "Ошибка во время генерации ответа."
}

err_invalid_argument = {
    'en': "Invalid command argument. Usage: /share <download_id>",
    'ru': "Недопустимый аргумент команды. Использование: /share <download_id>"
}

err_invalid_data_type = {
    'en': "Invalid data type.",
    'ru': "Недопустимый тип данных."
}

err_unavailable_to_share = {
    'en': "Unavailable to share.",
    'ru': "Невозможно поделиться."
}

# Choosing formats

video = {
    'en': 'Video',
    'ru': 'Видео',
}

audio = {
    'en': 'Audio',
    'ru': 'Аудио',
}

choose_extension = {
    'en': 'Choose extension',
    'ru': 'Выберете расширение',
}

extension = {
    'en': 'Extension',
    'ru': 'Расширение',
}

choose_quality = {
    'en': 'Choose quality',
    'ru': 'Выберете качество',
}

quality = {
    'en': 'Quality',
    'ru': 'Качество',
}

back = {
    'en': 'Back',
    'ru': 'Назад',
}

download = {
    'en': 'Download',
    'ru': 'Скачать',
}

filesize = {
    'en': 'Filesize',
    'ru': 'Размер файла',
}

mb = {
    'en': 'MB',
    'ru': 'МБ',
}

caption = {
    'en': 'Caption',
    'ru': 'Подпись',
}

source = {
    'en': 'Source',
    'ru': 'Источник',
}
