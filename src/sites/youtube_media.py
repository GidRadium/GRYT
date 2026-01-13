import src.sites.site_base as base
import re
from src.logger import logger

import yt_dlp

COOKIES = "YOUTUBE_COOKIES from .env"
PROXIES = [
    "MEDIA_PROXY from .env",
    "",
]

class YouTubeAudioStream:
    stream_id: str = ""
    extension: str = ""
    codec: str = ""
    size_bytes: int = 0
    bitrate_kbit_per_s: int = 0
    language: str = ""

    def __str__(self) -> str:
        return f"{self.stream_id}|{self.language}|{self.extension}|{self.codec}|{self.bitrate_kbit_per_s}Kbit/s|{round(float(self.size_bytes)/1048576)}Mb"

class YouTubeVideoStream:
    stream_id: str = ""
    extension: str = ""
    codec: str = ""
    size_bytes: int = 0
    height: int = 0
    width: int = 0
    fps: int = 0

    def __str__(self) -> str:
        return f"{self.stream_id}|{self.extension}|{self.height}p{self.fps}|{self.codec}|{round(float(self.size_bytes)/1048576)}Mb"

class YouTubeMergedStream:
    stream_id: str = ""
    extension: str = ""
    acodec: str = ""
    vcodec: str = ""
    size_bytes: int = 0
    height: int = 0
    width: int = 0
    fps: int = 0
    language: str = ""

    def __str__(self) -> str:
        return f"{self.stream_id}|{self.language}|{self.extension}|{self.height}p{self.fps}|{self.vcodec}+{self.acodec}|{round(float(self.size_bytes)/1048576)}Mb"

class YouTubeMediaData(base.SiteData):
    link: str = ""
    id: str = ""
    title: str = ""
    thumbnail_url: str = ""
    description: str = ""
    duration_seconds: int = 0
    is_live = False
    media_type: str = ""
    author: str = ""

    audio_streams: list[YouTubeAudioStream] = list[YouTubeAudioStream]()
    video_streams: list[YouTubeVideoStream] = list[YouTubeVideoStream]()
    merged_streams: list[YouTubeMergedStream] = list[YouTubeMergedStream]()

    def __str__(self) -> str:
        result = f"""link: {self.link}
id: {self.id}
title: {self.title}
author: {self.author}
thumbnail_url: {self.thumbnail_url}
duration_seconds: {self.duration_seconds}
is_live: {self.is_live}
media_type: {self.media_type}
len(description): {len(self.description)}
"""
        result += f"audio_streams ({len(self.audio_streams)}):\n"
        for stream in self.audio_streams:
            result += f"{stream}\n"
        result += f"video_streams ({len(self.video_streams)}):\n"
        for stream in self.video_streams:
            result += f"{stream}\n"
        result += f"merged_streams ({len(self.merged_streams)}):\n"
        for stream in self.merged_streams:
            result += f"{stream}\n"
        return result


class YouTubeMediaPreparedData(base.SitePreparedData):
    pass

class YouTubeMediaAPI(base.SiteAPI):
    @staticmethod
    def supports(link: str) -> bool:
        return bool(re.match(
            (r'^(?:http|ftp)s?://('
            r'youtube\.com|'
            r'www\.youtube\.com|'
            r'youtu\.be|'
            r'music\.youtube\.com'
            r')/')
            , link))

    @staticmethod
    def get_data(link: str) -> tuple[YouTubeMediaData, dict]: # data, error_message
        logger.info(f"[YouTubeDashAPI.get_data({link})]")

        ydl_opts_base = {
            "quiet": True,
            "no_warnings": True,
            "dump_single_json": True,
            "skip_download": True,
            "extract_flat": False,
            "cookiefile": COOKIES
        }

        last_error = ""
        # used_proxy = ""
        info = None

        for proxy in PROXIES:
            opts = ydl_opts_base | {"proxy": proxy}
            ydl = None
            try:
                ydl = yt_dlp.YoutubeDL(opts) # type: ignore[arg-type]
                info = ydl.extract_info(link, download=False)
                logger.info(f"Proxy: {proxy}")
                break
            except Exception as e:
                last_error = str(e)
                continue
            finally:
                if ydl is not None:
                    ydl.close()

        if info is None:
            return YouTubeMediaData(), {"error": last_error}

        data = YouTubeMediaData()
        data.link = link
        data.id = info["id"]
        data.title = str(info["title"]) if "title" in info else ""
        data.thumbnail_url = str(info["thumbnail"]) if "thumbnail" in info else ""
        data.description = str(info["description"]) if "description" in info else ""
        data.duration_seconds = int(info["duration"] or "0") if "duration" in info else 0
        data.is_live = "is_live" in info and info["is_live"] == "True"
        data.media_type = str(info["media_type"]) if "media_type" in info else ""
        data.author = str(info["channel"]) if "channel" in info else ""

        if "formats" in info and info["formats"] is not None:
            for format in info["formats"]:
                if "acodec" not in format or "vcodec" not in format:
                    continue
                if format["acodec"] == "none" and format["vcodec"] == "none":
                    continue
                if format["acodec"] != "none" and format["vcodec"] == "none":
                    audio_stream = YouTubeAudioStream()
                    audio_stream.stream_id = format["format_id"]
                    audio_stream.extension = format["ext"]
                    audio_stream.codec = format["acodec"]
                    audio_stream.size_bytes = int(format["filesize"]) if "filesize" in format and str(format["filesize"]).isdigit() else int(format["filesize_approx"]) if "filesize_approx" in format and str(format["filesize_approx"]).isdigit() else 0
                    audio_stream.bitrate_kbit_per_s = int(audio_stream.size_bytes / (data.duration_seconds * 128))
                    audio_stream.language = format["language"]
                    data.audio_streams.append(audio_stream)
                if format["acodec"] == "none" and format["vcodec"] != "none":
                    video_stream = YouTubeVideoStream()
                    video_stream.stream_id = format["format_id"]
                    video_stream.extension = format["ext"]
                    video_stream.codec = format["vcodec"]
                    video_stream.size_bytes = int(format["filesize"]) if "filesize" in format and str(format["filesize"]).isdigit() else int(format["filesize_approx"]) if "filesize_approx" in format and str(format["filesize_approx"]).isdigit() else 0
                    video_stream.height = format["height"]
                    video_stream.width = format["width"]
                    video_stream.fps = int(format["fps"])
                    data.video_streams.append(video_stream)
                if format["acodec"] != "none" and format["vcodec"] != "none":
                    merged_stream = YouTubeMergedStream()
                    merged_stream.stream_id = format["format_id"]
                    merged_stream.extension = format["ext"]
                    merged_stream.acodec = format["acodec"]
                    merged_stream.vcodec = format["vcodec"]
                    merged_stream.size_bytes = int(format["filesize"]) if "filesize" in format and str(format["filesize"]).isdigit() else int(format["filesize_approx"]) if "filesize_approx" in format and str(format["filesize_approx"]).isdigit() else 0
                    if merged_stream.size_bytes == 0 and "tbr" in format:
                        try:
                            merged_stream.size_bytes = int(float(format["tbr"]) * data.duration_seconds * 128)
                        except:
                            pass
                    merged_stream.height = format["height"]
                    merged_stream.width = format["width"]
                    merged_stream.fps = int(format["fps"])
                    merged_stream.language = format["language"]
                    data.merged_streams.append(merged_stream)

        logger.info(data)


        return YouTubeMediaData(), dict()
