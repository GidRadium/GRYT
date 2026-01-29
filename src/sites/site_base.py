import src.translations as s
from src.user_settings import UserSettings

class SiteData:
    # content_type = ContentTypes.DEFAULT
    pass

class SitePreparedData:
    # content_type = ContentTypes.DEFAULT
    # filesize: int = None
    # download_text: str = ""
    # log_text: str = ""
    # caption = ""
    pass

class SiteAPI:
    # content_type = ContentTypes.DEFAULT

    @staticmethod
    def supports(link: str) -> bool:
        return False

    @staticmethod
    def get_data(link: str) -> tuple[SiteData, dict]: # data, error_message
        return SiteData(), s.err_not_defined

    @staticmethod
    def get_w_h_to_trim_thumb(data: SiteData) -> tuple[int, int]:
        return 0, 0

    @staticmethod
    def generate_response(data: SiteData, query: str, request_id: int, user_settings: UserSettings) -> tuple[str, list[list[tuple[str, str]]], dict|None]: # text, buttons_data, error_message
        return "", list[list[tuple[str, str]]](), s.err_not_defined

    @staticmethod
    def get_image_url(data: SiteData) -> str:
        return ""

    @staticmethod
    def prepare_to_download(data: SiteData, query: str, user_settings: UserSettings) -> SitePreparedData:
        return SitePreparedData()

    # @staticmethod
    # def download(prepared_data: SitePreparedData, progress: Progress = None) -> tuple[ContentTypeBase, dict]: # result, error_message
    #     return None, s.err_not_defined
