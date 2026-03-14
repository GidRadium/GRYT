from __future__ import annotations
import re
from io import StringIO
from dataclasses import dataclass, field
from typing import Any
from html import escape

import yt_dlp

import src.sites.site_base as base
from src.logger import logger
from src.enviroment import MEDIA_PROXY, YOUTUBE_COOKIES
from src.user_settings import UserSettings
import src.translations as s


COOKIES = YOUTUBE_COOKIES
PROXIES = ["", MEDIA_PROXY]
# PROXIES = [""]

@dataclass
class YouTubeAudioStream:
    stream_id: str = ""
    extension: str = ""
    codec: str = ""
    size_bytes: int = 0
    bitrate_kbit_per_s: int = 0
    language: str = ""

    def __str__(self) -> str:
        return (
            f"{self.stream_id}.{self.language}.{self.extension}."
            f"{self.codec[:4]}."
            f"{self.bitrate_kbit_per_s}Kbit/s."
            f"{round(float(self.size_bytes) / 1048576)}Mb"
        )


@dataclass
class YouTubeVideoStream:
    stream_id: str = ""
    extension: str = ""
    codec: str = ""
    size_bytes: int = 0
    height: int = 0
    width: int = 0
    fps: int = 0

    def __str__(self) -> str:
        return (
            f"{self.stream_id}.{self.height}p{self.fps}.{self.extension}."
            f"{self.codec[:4]}.{round(float(self.size_bytes) / 1048576)}Mb"
        )


@dataclass
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
        return (
            f"{self.stream_id}.{self.language}.{self.extension}."
            f"{self.height}p{self.fps}.{self.vcodec[:4]}+{self.acodec[:4]}."
            f"{round(float(self.size_bytes) / 1048576)}Mb"
        )


@dataclass
class YouTubeMediaData(base.SiteData):
    link: str = ""
    id: str = ""
    title: str = ""
    thumbnail_url: str = ""
    description: str = ""
    duration_seconds: int = 0
    is_live: bool = False
    media_type: str = ""
    author: str = ""

    audio_streams: list[YouTubeAudioStream] = field(default_factory=list)
    video_streams: list[YouTubeVideoStream] = field(default_factory=list)
    merged_streams: list[YouTubeMergedStream] = field(default_factory=list)

    def __str__(self) -> str:
        buf = StringIO()

        buf.write(
            f"link: {self.link}\n"
            f"id: {self.id}\n"
            f"title: {self.title}\n"
            f"author: {self.author}\n"
            f"thumbnail_url: {self.thumbnail_url}\n"
            f"duration_seconds: {self.duration_seconds}\n"
            f"is_live: {self.is_live}\n"
            f"media_type: {self.media_type}\n"
            f"len(description): {len(self.description)}\n"
        )

        for name, items in [
            ("audio_streams", self.audio_streams),
            ("video_streams", self.video_streams),
            ("merged_streams", self.merged_streams),
        ]:
            buf.write(f"{name} ({len(items)}):\n")
            for item in items:
                buf.write(f"{item}\n")

        return buf.getvalue()


class YouTubeMediaPreparedData(base.SitePreparedData):
    pass


class YouTubeMediaAPI(base.SiteAPI):

    @staticmethod
    def supports(link: str) -> bool:
        return bool(
            re.match(
                r'^(?:http|ftp)s?://('
                r'youtube\.com|'
                r'www\.youtube\.com|'
                r'youtu\.be|'
                r'music\.youtube\.com'
                r')/',
                link
            )
        )

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    @staticmethod
    def get_data(link: str) -> tuple[YouTubeMediaData, dict]:
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
        info = None

        for proxy in PROXIES:
            opts = {**ydl_opts_base, "proxy": proxy}
            ydl = None
            try:
                ydl = yt_dlp.YoutubeDL(opts)  # type: ignore[arg-type]
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
        data.id = info.get("id", "")
        data.title = str(info.get("title", ""))
        data.thumbnail_url = str(info.get("thumbnail", ""))
        data.description = str(info.get("description", ""))
        data.duration_seconds = YouTubeMediaAPI._safe_int(info.get("duration", 0))
        data.is_live = bool(info.get("is_live", False))
        data.media_type = str(info.get("media_type", ""))
        data.author = str(info.get("channel", ""))

        formats = info.get("formats") or []

        for fmt in formats:

            acodec = fmt.get("acodec", "none")
            vcodec = fmt.get("vcodec", "none")

            # Useless streams
            if acodec == "none" and vcodec == "none":
                continue

            size = (
                YouTubeMediaAPI._safe_int(fmt.get("filesize"))
                or YouTubeMediaAPI._safe_int(fmt.get("filesize_approx"))
                or 0
            )

            # Audio only
            if acodec != "none" and vcodec == "none":
                audio_stream = YouTubeAudioStream()
                audio_stream.stream_id = fmt.get("format_id", "")
                audio_stream.extension = fmt.get("ext", "")
                audio_stream.codec = acodec
                audio_stream.size_bytes = size
                audio_stream.bitrate_kbit_per_s = int(size / (128 * data.duration_seconds)) if data.duration_seconds > 0 and size > 0 else 0
                audio_stream.language = fmt.get("language", "") or ""
                data.audio_streams.append(audio_stream)

            # Video only
            elif acodec == "none" and vcodec != "none":
                video_stream = YouTubeVideoStream()
                video_stream.stream_id = fmt.get("format_id", "")
                video_stream.extension = fmt.get("ext", "")
                video_stream.codec = vcodec
                video_stream.size_bytes = size
                video_stream.height = YouTubeMediaAPI._safe_int(fmt.get("height", 0))
                video_stream.width = YouTubeMediaAPI._safe_int(fmt.get("width", 0))
                video_stream.fps = YouTubeMediaAPI._safe_int(fmt.get("fps", 0))
                data.video_streams.append(video_stream)

            # Merged Video+Audio
            else:
                merged_stream = YouTubeMergedStream()
                merged_stream.stream_id = fmt.get("format_id", "")
                merged_stream.extension = fmt.get("ext", "")
                merged_stream.acodec = acodec
                merged_stream.vcodec = vcodec
                merged_stream.size_bytes = size or int(YouTubeMediaAPI._safe_float(fmt.get("tbr", 0.0)) * 128 * data.duration_seconds)
                merged_stream.height = YouTubeMediaAPI._safe_int(fmt.get("height", 0))
                merged_stream.width = YouTubeMediaAPI._safe_int(fmt.get("width", 0))
                merged_stream.fps = YouTubeMediaAPI._safe_int(fmt.get("fps", 0))
                merged_stream.language = fmt.get("language", "") or ""
                data.merged_streams.append(merged_stream)

        logger.info(data)

        return data, {}

    @staticmethod
    def generate_response(data: base.SiteData, query: str, request_id: int, user_settings: UserSettings) -> tuple[str, list[list[tuple[str, str]]], dict|None]: # text, buttons_data, error_message
        if not isinstance(data, YouTubeMediaData):
            return "", [], s.err_invalid_data_type
        yt_data: YouTubeMediaData = data
        lang = user_settings.default_language
        # query: "v1 [type](v/a/.) [stream](str/sv+sa/.) [language](ab/.)" . == None
        query_splitted = query.split(" ")
        buttons_data = []
        caption = "text"

        # Generage default buttons
        if ((query == "" and not user_settings.defaulf_suggest_more_streams)) or query.startswith("v1"):
            v, stream_type, stream_id, stream_language = query_splitted if len(query_splitted) == 4 else ["v1", ".", ".", "."]

            # Get all media languages
            media_languages: list[str] = []
            for audio_stream in yt_data.audio_streams:
                if audio_stream.language and audio_stream.language not in media_languages:
                    media_languages.append(audio_stream.language)

            # Create a button to switch languages
            if len(media_languages) > 1:
                if stream_language == ".":
                    stream_language = media_languages[0]
                new_stream_language = media_languages[(media_languages.index(stream_language) + 1) % len(media_languages)]
                language_text = f"{s.default_language[lang]}:"
                for lng in media_languages:
                    language_text += f" 【{lng}】" if lng == stream_language else f" {lng}"

                new_audio_stream_id = ""
                new_stream_id = stream_id
                if stream_type == "a" or "+" in stream_id:
                    for audio_stream in yt_data.audio_streams:
                        if audio_stream.extension == "m4a" and audio_stream.language == new_stream_language:
                            new_audio_stream_id = audio_stream.stream_id

                    new_stream_id = new_audio_stream_id if stream_type == "a" else f"{stream_id.split('+')[0]}+{new_audio_stream_id}"

                language_callback = f"clarify {request_id} {v} {stream_type} {new_stream_id} {new_stream_language}"

                buttons_data.append([(language_text, language_callback)])

            # Get best video streams
            video_streams_id_in_data: dict[int, int] = dict()
            for i in range(len(yt_data.video_streams)):
                if yt_data.video_streams[i].extension == "mp4":
                    video_streams_id_in_data[yt_data.video_streams[i].height] = i

            # Get best audio stream
            audio_stream_id_in_data = -1
            for i in range(len(yt_data.audio_streams)):
                if yt_data.audio_streams[i].extension == "m4a" and (len(media_languages) <= 1 or yt_data.audio_streams[i].language == stream_language):
                    audio_stream_id_in_data = i

            # Generate video buttons data
            v_streams_count = 0
            buttons_data_row = [("---", "empty"), ("---", "empty")]
            for i in video_streams_id_in_data.values():
                size_bytes = (yt_data.video_streams[i].size_bytes + yt_data.audio_streams[audio_stream_id_in_data].size_bytes)
                if size_bytes > 2*1024*1024*1024:
                    continue

                new_stream_id = f"{yt_data.video_streams[i].stream_id}+{yt_data.audio_streams[audio_stream_id_in_data].stream_id}"
                video_button_text = f"{yt_data.video_streams[i].height}p{yt_data.video_streams[i].fps} | {round(size_bytes / (1024 * 1024))} Mb"
                if new_stream_id != stream_id:
                    buttons_data_row[v_streams_count % 2] = (
                        video_button_text,
                        f"clarify {request_id} {v} v {new_stream_id} {stream_language}"
                    )
                else:
                    buttons_data_row[v_streams_count % 2] = (
                        f"✅ {video_button_text}",
                        f"clarify {request_id} {v} . . {stream_language}"
                    )

                if v_streams_count % 2:
                    buttons_data.append(buttons_data_row)
                    buttons_data_row = [("---", "empty"), ("---", "empty")]

                v_streams_count += 1

            if v_streams_count % 2:
                buttons_data.append(buttons_data_row)

            # Generate audio button data
            if yt_data.audio_streams[audio_stream_id_in_data].size_bytes < 2*1024*1024*1024:
                audio_button_text = f"Only audio | {round(yt_data.audio_streams[audio_stream_id_in_data].size_bytes / (1024 * 1024))} Mb"
                if stream_type != "a":
                    audio_button_data = (
                        f"{audio_button_text}",
                        f"clarify {request_id} {v} a {yt_data.audio_streams[audio_stream_id_in_data].stream_id} {stream_language}"
                    )
                else:
                    audio_button_data = (
                        f"✅ {audio_button_text}",
                        f"clarify {request_id} {v} . . {stream_language}"
                    )

                buttons_data.append([audio_button_data])

                if stream_type == ".":
                    buttons_data.append([("More streams", f"clarify {request_id} v2")])
                else:
                    buttons_data.append([(
                        "📥 Download 📥",
                        f"download {request_id} {v} {stream_type} {stream_id} {stream_language}"
                    )])

            # Generate text between image and buttons
            caption = f"<b>{escape(yt_data.title)}</b>\n<em>{escape(yt_data.author)}</em>"

        # query = "v2"

        return caption, buttons_data, None

    @staticmethod
    def get_image_url(data: base.SiteData) -> str:
        if not isinstance(data, YouTubeMediaData):
            return ""

        yt_data: YouTubeMediaData = data
        return yt_data.thumbnail_url
