from __future__ import annotations
import re
import src.sites.site_base as base
from src.logger import logger
from src.enviroment import MEDIA_PROXY, YOUTUBE_COOKIES
from io import StringIO

from dataclasses import dataclass, field
from typing import Any
import yt_dlp

COOKIES = YOUTUBE_COOKIES
PROXIES = [MEDIA_PROXY, ""]

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

        # ВАЖНО: возвращаем СФОРМИРОВАННЫЙ объект
        return data, {}
