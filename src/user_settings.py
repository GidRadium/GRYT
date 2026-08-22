import src.translations as s


class UserSettings:
    telegram_user_id: int = 0
    default_language: str = "en"
    default_audio_caption: str = "source"
    default_video_caption: str = "title+source"
    default_post_caption: str = "source"
    default_share_status: bool = False
    defaulf_suggest_more_streams: bool = False
    allow_press_buttons: bool = False
    show_less_steam_count: bool = False
